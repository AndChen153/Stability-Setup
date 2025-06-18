"""
Application State Management Module

Centralizes application state management with proper encapsulation.
Replaces scattered state variables throughout the application.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal
from gui.trial_manager.preset_data_class import Preset, Trial
from constants import Mode


class ApplicationStatus(Enum):
    """Application status enumeration."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class MeasurementState:
    """State information for current measurement."""
    mode: Optional[Mode] = None
    preset: Optional[Preset] = None
    current_trial: Optional[Trial] = None
    trial_queue: List[Trial] = field(default_factory=list)
    trial_directory: str = ""
    start_time: Optional[float] = None
    
    def is_running(self) -> bool:
        """Check if measurement is currently running."""
        return self.mode is not None and self.current_trial is not None
    
    def clear(self) -> None:
        """Clear measurement state."""
        self.mode = None
        self.preset = None
        self.current_trial = None
        self.trial_queue.clear()
        self.trial_directory = ""
        self.start_time = None


@dataclass
class ArduinoState:
    """State information for Arduino connections."""
    connected_devices: List[str] = field(default_factory=list)
    unknown_devices: List[str] = field(default_factory=list)
    device_count: int = 0
    initialization_successful: bool = False
    
    def is_valid(self) -> bool:
        """Check if Arduino state is valid for measurements."""
        return self.initialization_successful and self.device_count > 0
    
    def clear(self) -> None:
        """Clear Arduino state."""
        self.connected_devices.clear()
        self.unknown_devices.clear()
        self.device_count = 0
        self.initialization_successful = False


class ApplicationState(QObject):
    """
    Centralized application state manager.
    
    Manages all application state with proper encapsulation and signals.
    Provides a single source of truth for application status.
    """
    
    # Signals for state changes
    status_changed = Signal(ApplicationStatus)
    measurement_started = Signal(Trial)
    measurement_finished = Signal()
    arduino_state_changed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._status = ApplicationStatus.IDLE
        self.measurement = MeasurementState()
        self.arduino = ArduinoState()
        self._error_message = ""
    
    @property
    def status(self) -> ApplicationStatus:
        """Get current application status."""
        return self._status
    
    @status.setter
    def status(self, value: ApplicationStatus) -> None:
        """Set application status and emit signal."""
        if self._status != value:
            self._status = value
            self.status_changed.emit(value)
    
    @property
    def error_message(self) -> str:
        """Get current error message."""
        return self._error_message
    
    def set_error(self, message: str) -> None:
        """Set error state with message."""
        self._error_message = message
        self.status = ApplicationStatus.ERROR
        self.error_occurred.emit(message)
    
    def clear_error(self) -> None:
        """Clear error state."""
        self._error_message = ""
        if self.status == ApplicationStatus.ERROR:
            self.status = ApplicationStatus.IDLE
    
    def start_measurement(self, preset: Preset) -> bool:
        """
        Start a measurement with the given preset.
        
        Args:
            preset: The preset to run
            
        Returns:
            True if measurement started successfully, False otherwise
        """
        if self.status != ApplicationStatus.IDLE:
            self.set_error(f"Cannot start measurement: application is {self.status.value}")
            return False
        
        if not self.arduino.is_valid():
            self.set_error("Cannot start measurement: Arduino not properly initialized")
            return False
        
        if not preset.trials:
            self.set_error("Cannot start measurement: preset has no trials")
            return False
        
        # Set up measurement state
        self.measurement.preset = preset
        self.measurement.trial_queue = preset.trials.copy()
        self.measurement.current_trial = self.measurement.trial_queue.pop(0)
        self.measurement.mode = self.measurement.current_trial.trial_type
        
        import time
        self.measurement.start_time = time.time()
        
        self.status = ApplicationStatus.RUNNING
        self.measurement_started.emit(self.measurement.current_trial)
        
        return True
    
    def next_trial(self) -> Optional[Trial]:
        """
        Move to the next trial in the queue.
        
        Returns:
            Next trial if available, None if queue is empty
        """
        if not self.measurement.trial_queue:
            return None
        
        self.measurement.current_trial = self.measurement.trial_queue.pop(0)
        self.measurement.mode = self.measurement.current_trial.trial_type
        
        return self.measurement.current_trial
    
    def finish_measurement(self) -> None:
        """Finish current measurement."""
        if self.status == ApplicationStatus.RUNNING:
            self.measurement.clear()
            self.status = ApplicationStatus.IDLE
            self.measurement_finished.emit()
    
    def stop_measurement(self) -> None:
        """Stop current measurement."""
        if self.status == ApplicationStatus.RUNNING:
            self.status = ApplicationStatus.STOPPING
            # Actual stopping logic will be handled by controllers
    
    def update_arduino_state(self, 
                           connected_devices: List[str],
                           unknown_devices: List[str] = None,
                           initialization_successful: bool = False) -> None:
        """
        Update Arduino connection state.
        
        Args:
            connected_devices: List of connected device IDs
            unknown_devices: List of unknown device IDs
            initialization_successful: Whether initialization was successful
        """
        self.arduino.connected_devices = connected_devices.copy()
        self.arduino.unknown_devices = (unknown_devices or []).copy()
        self.arduino.device_count = len(connected_devices)
        self.arduino.initialization_successful = initialization_successful
        
        self.arduino_state_changed.emit()
    
    def set_trial_directory(self, directory: str) -> None:
        """Set the trial directory for data storage."""
        self.measurement.trial_directory = directory
    
    def get_status_text(self) -> str:
        """Get human-readable status text."""
        status_texts = {
            ApplicationStatus.IDLE: "Ready",
            ApplicationStatus.INITIALIZING: "Initializing...",
            ApplicationStatus.RUNNING: "Running measurement",
            ApplicationStatus.STOPPING: "Stopping...",
            ApplicationStatus.ERROR: f"Error: {self.error_message}"
        }
        return status_texts.get(self.status, "Unknown")
    
    def get_measurement_info(self) -> Dict[str, Any]:
        """Get current measurement information."""
        if not self.measurement.is_running():
            return {}
        
        return {
            "preset_name": self.measurement.preset.name if self.measurement.preset else "",
            "current_trial": self.measurement.current_trial.trial_type.name if self.measurement.current_trial else "",
            "trials_remaining": len(self.measurement.trial_queue),
            "trial_directory": self.measurement.trial_directory,
            "start_time": self.measurement.start_time
        }
    
    def is_busy(self) -> bool:
        """Check if application is busy (not idle)."""
        return self.status != ApplicationStatus.IDLE
