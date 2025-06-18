"""
Measurement Service Module

High-level service for managing measurement operations.
Provides a clean interface between GUI and controller layers.
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from constants import Mode
from gui.trial_manager.preset_data_class import Preset, Trial
from controller.multi_arduino_controller import MultiController
from core.config_manager import ConfigManager
from core.application_state import ApplicationState, ApplicationStatus
from core.error_handler import get_error_handler, with_error_handling
from core.thread_manager import get_thread_manager
from helper.global_helpers import get_logger


class MeasurementService(QObject):
    """
    High-level service for measurement operations.
    
    Provides a clean interface for starting, stopping, and monitoring measurements.
    Handles coordination between GUI, state management, and Arduino controllers.
    """
    
    measurement_started = Signal(Trial)
    measurement_finished = Signal()
    measurement_progress = Signal(str)  # Progress message
    trial_completed = Signal(Trial)
    preset_completed = Signal(Preset)
    
    def __init__(self, config_manager: ConfigManager, app_state: ApplicationState):
        super().__init__()
        self.config = config_manager
        self.app_state = app_state
        self.controller = MultiController()
        self.error_handler = get_error_handler()
        self.thread_manager = get_thread_manager()
        
        # Connect signals
        self.controller.started.connect(self._on_measurement_started)
        self.controller.finished.connect(self._on_measurement_finished)
        self.app_state.status_changed.connect(self._on_status_changed)
        
        # Current measurement tracking
        self._current_task_id: Optional[str] = None
    
    @with_error_handling(get_error_handler(), "Arduino initialization", return_value=False)
    def initialize_arduinos(self, trial_name: str = "") -> bool:
        """
        Initialize Arduino connections.
        
        Args:
            trial_name: Optional trial name for data directory
            
        Returns:
            True if initialization successful, False otherwise
        """
        self.app_state.status = ApplicationStatus.INITIALIZING
        
        get_logger().log("Initializing Arduino connections...")
        
        # Get data directory
        data_dir = self.config.get_data_directory(trial_name)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize controller
        result = self.controller.initializeMeasurement(
            trial_name=trial_name,
            data_dir=str(data_dir.parent),
            email=self.config.email.user if self.config.email.is_valid() else "",
            email_user=self.config.email.user,
            email_pass=self.config.email.password,
            date=data_dir.name,
            json_location=str(self.config.config_file),
            plotting_mode=False
        )
        
        # Update application state
        if result:
            self.app_state.update_arduino_state(
                connected_devices=self.controller.connected_arduinos_HWID,
                unknown_devices=self.controller.unknownID,
                initialization_successful=True
            )
            self.app_state.set_trial_directory(str(data_dir))
            self.app_state.status = ApplicationStatus.IDLE
            get_logger().log("Arduino initialization successful")
        else:
            self.app_state.update_arduino_state(
                connected_devices=self.controller.connected_arduinos_HWID,
                unknown_devices=self.controller.unknownID,
                initialization_successful=False
            )
            self.app_state.set_error("Arduino initialization failed")
            get_logger().log("Arduino initialization failed")
        
        return result
    
    @with_error_handling(get_error_handler(), "Starting measurement", return_value=False)
    def start_measurement(self, preset: Preset) -> bool:
        """
        Start a measurement with the given preset.
        
        Args:
            preset: The preset to execute
            
        Returns:
            True if measurement started successfully, False otherwise
        """
        # Validate state
        if not self.app_state.arduino.is_valid():
            self.error_handler.error("Cannot start measurement: Arduino not initialized")
            return False
        
        if self.app_state.is_busy():
            self.error_handler.error(f"Cannot start measurement: application is {self.app_state.status.value}")
            return False
        
        # Start measurement in application state
        if not self.app_state.start_measurement(preset):
            return False
        
        # Execute first trial
        return self._execute_current_trial()
    
    def _execute_current_trial(self) -> bool:
        """Execute the current trial."""
        current_trial = self.app_state.measurement.current_trial
        if not current_trial:
            self.error_handler.error("No current trial to execute")
            return False
        
        get_logger().log(f"Starting trial: {current_trial.trial_type.name}")
        
        # Submit trial execution as background task
        self._current_task_id = self.thread_manager.submit_task(
            self._run_trial,
            current_trial,
            task_name=f"Trial: {current_trial.trial_type.name}"
        )
        
        return True
    
    def _run_trial(self, trial: Trial) -> None:
        """Run a single trial (executed in background thread)."""
        try:
            # Run the trial
            self.controller.run(trial.trial_type, trial.params)
            
        except Exception as e:
            self.error_handler.handle_exception(e, "Trial execution failed")
            raise
    
    def _on_measurement_started(self) -> None:
        """Handle measurement started signal from controller."""
        current_trial = self.app_state.measurement.current_trial
        if current_trial:
            self.measurement_started.emit(current_trial)
            self.measurement_progress.emit(f"Running {current_trial.trial_type.name}")
    
    def _on_measurement_finished(self) -> None:
        """Handle measurement finished signal from controller."""
        current_trial = self.app_state.measurement.current_trial
        if current_trial:
            self.trial_completed.emit(current_trial)
            get_logger().log(f"Trial completed: {current_trial.trial_type.name}")
        
        # Check if there are more trials
        next_trial = self.app_state.next_trial()
        if next_trial:
            # Start next trial
            get_logger().log(f"Starting next trial: {next_trial.trial_type.name}")
            self._execute_current_trial()
        else:
            # All trials completed
            preset = self.app_state.measurement.preset
            self.app_state.finish_measurement()
            
            if preset:
                self.preset_completed.emit(preset)
                get_logger().log(f"Preset completed: {preset.name}")
            
            self.measurement_finished.emit()
    
    def _on_status_changed(self, status: ApplicationStatus) -> None:
        """Handle application status changes."""
        status_messages = {
            ApplicationStatus.IDLE: "Ready",
            ApplicationStatus.INITIALIZING: "Initializing Arduino connections...",
            ApplicationStatus.RUNNING: "Running measurement...",
            ApplicationStatus.STOPPING: "Stopping measurement...",
            ApplicationStatus.ERROR: f"Error: {self.app_state.error_message}"
        }
        
        message = status_messages.get(status, "Unknown status")
        self.measurement_progress.emit(message)
    
    @with_error_handling(get_error_handler(), "Stopping measurement")
    def stop_measurement(self) -> None:
        """Stop the current measurement."""
        if not self.app_state.measurement.is_running():
            self.error_handler.warning("No measurement is currently running")
            return
        
        get_logger().log("Stopping measurement...")
        self.app_state.stop_measurement()
        
        # Cancel current task
        if self._current_task_id:
            self.thread_manager.cancel_task(self._current_task_id)
            self._current_task_id = None
        
        # Stop controller
        self.controller.run(Mode.STOP)
        
        # Reset state
        self.app_state.finish_measurement()
        self.measurement_finished.emit()
    
    def get_measurement_status(self) -> Dict[str, Any]:
        """Get current measurement status information."""
        return {
            "status": self.app_state.status.value,
            "is_running": self.app_state.measurement.is_running(),
            "arduino_connected": self.app_state.arduino.is_valid(),
            "device_count": self.app_state.arduino.device_count,
            **self.app_state.get_measurement_info()
        }
    
    def reset_arduinos(self) -> bool:
        """Reset Arduino connections."""
        try:
            self.controller.reset_arduinos()
            get_logger().log("Arduino connections reset")
            return True
        except Exception as e:
            self.error_handler.handle_exception(e, "Failed to reset Arduino connections")
            return False
    
    def get_connected_devices(self) -> List[str]:
        """Get list of connected Arduino devices."""
        return self.app_state.arduino.connected_devices.copy()
    
    def get_unknown_devices(self) -> List[str]:
        """Get list of unknown Arduino devices."""
        return self.app_state.arduino.unknown_devices.copy()
    
    def is_ready_for_measurement(self) -> bool:
        """Check if system is ready for measurement."""
        return (
            self.app_state.status == ApplicationStatus.IDLE and
            self.app_state.arduino.is_valid()
        )
