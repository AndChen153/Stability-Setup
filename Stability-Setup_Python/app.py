
# app.py
"""
Main application entry point for the Stability Measurement System.
Refactored for better separation of concerns and maintainability.
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QMessageBox,
    QStatusBar,
    QStyleFactory,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QIcon, QPalette, QColor

from helper.global_helpers import get_logger
from gui.arduino_manager.id_widget import IDWidget
from gui.results_viewer.plotter_panel import PlotterPanel
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.preset_window_widget import PresetQueueWidget
from core.config_manager import ConfigManager
from core.application_state import ApplicationState

# TODO: fix light/dark button
# TODO: Add metrics for JV scan
# TODO: add box plots
# TODO: limit measurements per mppt to account for measurement time
# TODO: limit time to 1000 hours for millis wrap around
# TODO: add collected printouts for setup phase of measurements


# TODO: better control over which arduino is running what, i.e. 8 total devices, run 8, stop 4, start 4 again
# TODO: dynamic visualization of data, live plotting
# TODO: live control over arduino settings, i.e. change mppt step size mid trial
# TODO: fix incosistencies between plotter widget and raw data
# TODO: add notification whenever anything stops running
# TODO: fix trial titles


# TODO: display metrics on logger page

#PAPER
#TODO: box plot for PCE between litos and my setup, 3-4 minute test
# collect PCE with litos, my setup, then litos again to show difference between litos and my setup might be due to device degrading
# PCE DATA: plot pce, current density, voltage, compared to time


# TOP of plots: JV comparison 2 pixels, PCE comparison 2 pixels, Box plot comparison PCE between litos and stability setup
# 2nd row: long panel which has stability for 1000 hours


#box plots: fill factor, jsc, voc, pce (From scan), stabilized PCE

# long term stability

class MainWindow(QMainWindow):
    """
    Main application window with improved architecture.

    Focuses on UI coordination and delegates business logic to service layer.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stability Measurement System")

        # Initialize core components
        self._init_core_components()

        # Initialize UI
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Initialize Arduino connections
        self._initialize_system()

    def _init_core_components(self) -> None:
        """Initialize core application components."""
        # Configuration
        config_file = Path(__file__).parent / "userSettings.json"
        self.config = ConfigManager(config_file)

        # Application state
        self.app_state = ApplicationState()

        # Error handling
        from core.error_handler import ErrorHandler, set_error_handler
        self.error_handler = ErrorHandler(self)
        set_error_handler(self.error_handler)

        # Services
        from services.measurement_service import MeasurementService
        self.measurement_service = MeasurementService(self.config, self.app_state)

    def _init_ui(self) -> None:
        """Initialize user interface components."""
        # Status tracking for UI updates
        self.marquee_timer = QTimer(self)
        self.marquee_timer.timeout.connect(self._update_marquee)
        self.marquee_text = "  Running...  "
        self.marquee_index = 0

        # Create main widgets
        self.ID_widget = IDWidget(str(self.config.config_file))
        self.preset_queue = PresetQueueWidget(str(self.config.config_file))

        # Data folder for plotter
        data_folder = self.config.data.base_dir
        self.plotter_panel = PlotterPanel(default_folder=data_folder)

        # Logger setup
        self._setup_logger()

        # Create tab widget
        self._create_tabs()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_logger(self) -> None:
        """Set up logging interface."""
        self.logger = get_logger()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.clear_button = QPushButton("Clear Logs")
        self.save_button = QPushButton("Save Logs")

        # Connect logger buttons
        self.clear_button.clicked.connect(self.logger.clear)
        self.save_button.clicked.connect(self._save_logs)

        logger_layout = QVBoxLayout()
        logger_layout.addWidget(self.text_edit)
        logger_layout.addWidget(self.clear_button)
        logger_layout.addWidget(self.save_button)

        self.logger_widget = QWidget()
        self.logger_widget.setLayout(logger_layout)
        self.logger.set_output_widget(self.text_edit)

    def _create_tabs(self) -> None:
        """Create main tab widget."""
        tabs = QTabWidget()
        tabs.addTab(self.preset_queue, "Trial Manager")
        tabs.addTab(self.ID_widget, "Arduino Manager")
        tabs.addTab(self.plotter_panel, "Results Viewer")
        tabs.addTab(self.logger_widget, "Log Viewer")

        self.setCentralWidget(tabs)

    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Arduino manager signals
        self.ID_widget.refreshRequested.connect(self._refresh_arduino_connections)

        # Preset queue signals
        self.preset_queue.run_start.connect(self._start_measurement)

        # Measurement service signals
        self.measurement_service.measurement_started.connect(self._on_measurement_started)
        self.measurement_service.measurement_finished.connect(self._on_measurement_finished)
        self.measurement_service.measurement_progress.connect(self._update_status)
        self.measurement_service.trial_completed.connect(self._on_trial_completed)
        self.measurement_service.preset_completed.connect(self._on_preset_completed)

        # Application state signals
        self.app_state.status_changed.connect(self._on_status_changed)
        self.app_state.arduino_state_changed.connect(self._on_arduino_state_changed)

    def _initialize_system(self) -> None:
        """Initialize system components."""
        self._refresh_arduino_connections()

    def _refresh_arduino_connections(self) -> None:
        """Refresh Arduino connections."""
        get_logger().log("Refreshing Arduino connections...")
        success = self.measurement_service.initialize_arduinos()

        if success:
            # Update UI with connection info
            self.ID_widget.connected_Arduino = self.measurement_service.get_connected_devices()
            self.ID_widget.refresh_ui()
            self.ID_widget.save_json()
        else:
            # Handle unknown devices
            unknown_devices = self.measurement_service.get_unknown_devices()
            if unknown_devices:
                for device_id in unknown_devices:
                    self.ID_widget.data[device_id] = -1
                self.ID_widget.save_json()
                self.ID_widget.refresh_ui()

    def _save_logs(self) -> None:
        """Save current logs to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"log_{timestamp}.txt"
        root_dir = Path(__file__).parent
        full_path = root_dir / filename

        get_logger().save(str(full_path))
        get_logger().log(f"Log saved to {full_path}")

    @Slot(Preset)
    def _start_measurement(self, preset: Preset) -> None:
        """Start measurement with given preset."""
        get_logger().log(f"Starting measurement: {preset.name}")
        self._refresh_arduino_connections()
        success = self.measurement_service.start_measurement(preset)
        if not success:
            QMessageBox.warning(
                self,
                "Measurement Error",
                "Failed to start measurement. Check Arduino connections and try again."
            )

    # Signal handlers for measurement service
    def _on_measurement_started(self, trial: Trial) -> None:
        """Handle measurement started."""
        get_logger().log(f"Measurement started: {trial.trial_type.name}")
        self._start_marquee()

        # Update plotter directory
        status = self.measurement_service.get_measurement_status()
        if "trial_directory" in status:
            self.plotter_panel.data_location_line_edit.setText(status["trial_directory"])

    def _on_measurement_finished(self) -> None:
        """Handle measurement finished."""
        get_logger().log("Measurement finished")
        self._stop_marquee()

    def _on_trial_completed(self, trial: Trial) -> None:
        """Handle trial completion."""
        get_logger().log(f"Trial completed: {trial.trial_type.name}")

    def _on_preset_completed(self, preset: Preset) -> None:
        """Handle preset completion."""
        QMessageBox.information(
            self,
            "Measurement Complete",
            f"Preset '{preset.name}' has finished successfully."
        )

    def _on_status_changed(self, status) -> None:
        """Handle application status changes."""
        # Update UI based on status
        pass

    def _on_arduino_state_changed(self) -> None:
        """Handle Arduino state changes."""
        # Update Arduino manager UI
        self.ID_widget.connected_Arduino = self.measurement_service.get_connected_devices()
        self.ID_widget.refresh_ui()

    def _update_status(self, message: str) -> None:
        """Update status bar with message."""
        if not self.app_state.measurement.is_running():
            self.status_bar.showMessage(message)

    # Marquee animation methods
    def _start_marquee(self) -> None:
        """Start marquee animation in status bar."""
        self.marquee_index = 0
        self.status_bar.showMessage(self.marquee_text)
        self.marquee_timer.start(200)

    def _stop_marquee(self) -> None:
        """Stop marquee animation."""
        self.marquee_timer.stop()
        self.status_bar.clearMessage()

    def _update_marquee(self) -> None:
        """Update marquee animation."""
        text_length = len(self.marquee_text)
        display_text = (
            self.marquee_text[self.marquee_index:] +
            self.marquee_text[:self.marquee_index]
        )
        self.status_bar.showMessage(display_text)
        self.marquee_index = (self.marquee_index - 1) % text_length

    # Legacy methods for compatibility (to be removed)
    def stop_action(self) -> None:
        """Stop current measurement (legacy method)."""
        self.measurement_service.stop_measurement()

    def closeEvent(self, event) -> None:
        """Handle application close event."""
        # Stop any running measurements
        if self.app_state.measurement.is_running():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A measurement is currently running. Do you want to stop it and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.measurement_service.stop_measurement()
            else:
                event.ignore()
                return

        # Shutdown thread manager
        from core.thread_manager import shutdown_thread_manager
        shutdown_thread_manager()

        # Save configuration
        self.config.save_config()

        event.accept()


if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)

    # Force Light mode
    app.setStyle(QStyleFactory.create("Fusion"))
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(255, 255, 255))
    light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Base, QColor(240, 240, 240))
    light_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
    light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))

    app.setPalette(light_palette)

    window = MainWindow()
    # window.showMaximized()
    window.setWindowIcon(QIcon(":/icons/logo.png"))
    window.setWindowTitle("Stability Measurement System")
    window.show()
    sys.exit(app.exec())
