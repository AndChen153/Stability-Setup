# app.py
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QMessageBox,
    QStatusBar,
    QSplitter,
    QStyleFactory,
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtCore import QSize, Signal, Slot, Qt
import assets_rc

from constants import Mode, Constants
from helper.global_helpers import custom_print
from controller.multi_arduino_controller import MultiController
from gui.arduino_manager.id_widget import IDWidget
from gui.results_viewer.plotter_panel import PlotterPanel
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.preset_window_widget import PresetQueueWidget
from gui.warning_popup import SelectionPopup
from controller import arduino_assignment

# TODO: fix light/dark button
# TODO: Add metrics for JV scan
# TODO: add box plots
# TODO: queue up measurements
# TODO: Create saved measurement combinations

# TODO: fix arduino mppt cell area value
# TODO: better control over which arduino is running what, i.e. 8 total devices, run 8, stop 4, start 4 again
# TODO: dynamic visualization of data, live plotting
# TODO: live control over arduino settings, i.e. change mppt step size mid trial
# TODO: dynamic step size optimization, gradient descent, optimizer algorithm that tries to find the maximum pce
# TODO: fix incosistencies between plotter widget and raw data

# TODO: fix null time error when plotting empty plot:

# Traceback (most recent call last):
#   File "c:\Users\MSE\Documents\GitHub\Stability-Setup\Stability-Setup_Python\gui\plotter_panel.py", line 72, in create_plots
#     self.update_plot_tabs(plot_groups)
#   File "c:\Users\MSE\Documents\GitHub\Stability-Setup\Stability-Setup_Python\gui\plotter_panel.py", line 88, in update_plot_tabs
#     plotter_widget.update_plot(title, filepaths)
#   File "c:\Users\MSE\Documents\GitHub\Stability-Setup\Stability-Setup_Python\gui\plotter_widget.py", line 61, in update_plot
#     self._plot_mppt(ax, csv_files, plot_title)
#   File "c:\Users\MSE\Documents\GitHub\Stability-Setup\Stability-Setup_Python\gui\plotter_widget.py", line 144, in _plot_mppt
#     overall_min_time = min(time)
# ValueError: min() arg is an empty sequence

#PAPER
#TODO: box plot for PCE between litos and my setup, 3-4 minute test
# collect PCE with litos, my setup, then litos again to show difference between litos and my setup might be due to device degrading
# PCE DATA: plot pce, current density, voltage, compared to time


# TOP of plots: JV comparison 2 pixels, PCE comparison 2 pixels, Box plot comparison PCE between litos and stability setup
# 2nd row: long panel which has stability for 1000 hours


class MainWindow(QMainWindow):
    next_trial_signal = Signal(Trial)

    def __init__(self):
        super().__init__()
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = os.path.join(self.base_dir, "data")
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.setWindowTitle("Stability Setup")
        # self.setGeometry(100, 100, 1200, 600)

        self.userSettingsJson = os.path.join(
            os.path.dirname(__file__), "userSettings.json"
        )

        # Running flags, button dictionaries, textboxes, etc.
        self.running_left = False
        self.running_plotter = False
        self.run_buttons = {}
        self.stop_buttons = {}
        self.textboxes = {}
        self.trial_name = ""  # Initialize shared Trial Name value
        self.trial_name_lineedits = []  # List to hold all Trial Name QLineEdits
        self.trial_queue = []
        self.running_preset: Preset = None
        self.running_mode = None
        self.next_trial_signal.connect(self.start_next_trial)

        # Email
        self.notification_email = None
        email_settings = self.load_json(self.userSettingsJson, "email_settings")
        self.email_user = email_settings["user"]
        self.email_pass = email_settings["pass"]

        # CSV watcher, thread control, etc.
        self.csv_watcher = QFileSystemWatcher()
        self.csv_watcher.fileChanged.connect(self.on_csv_changed)
        self.csv_watcher.directoryChanged.connect(self.on_csv_changed)
        self.running_thread = None
        self.stop_measurement_thread = threading.Event()

        self.multi_controller = MultiController()
        self.multi_controller.started.connect(self.load_plotter_dir)
        self.multi_controller.finished.connect(self.after_run)
        self.folder_path = None
        self.estimated_devices = max(1, len(arduino_assignment.get()))
        self.toggle_button = None

        self.ID_widget = IDWidget(self.userSettingsJson)
        self.ID_widget.refreshRequested.connect(self.initializeArduinoConnections)

        # Connect each SetupTab's signals to the MainWindow's action handlers.
        # self.setup_tabs.connect_signals(self.run_action, self.stop_action)

        self.preset_queue = PresetQueueWidget(self.userSettingsJson)
        self.preset_queue.run_start.connect(self.run_handler)
        #TODO: add stop handler


        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_folder_path = os.path.join(parent_dir, "data")

        self.plotter_panel = PlotterPanel(
            default_folder=data_folder_path
        )

        tabs = QTabWidget()
        tabs.addTab(self.preset_queue, Constants.trial_manager)
        tabs.addTab(self.ID_widget, Constants.arduino_manager)
        tabs.addTab(self.plotter_panel, Constants.results_viewer)

        self.setCentralWidget(tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Prepare marquee animation
        self.marquee_timer = QTimer(self)
        self.marquee_timer.timeout.connect(self.update_marquee)

        # The text to animate (leading/trailing spaces can help the effect)
        self.marquee_text = "  Running...  "
        self.marquee_index = 0

        self.initializeArduinoConnections()

    def initializeArduinoConnections(self):
        custom_print("Called Init Arduino Connection")
        result = self.multi_controller.initializeMeasurement(
            trial_name=self.trial_name,
            data_dir=self.data_dir,
            email=self.notification_email,
            email_user=self.email_user,
            email_pass=self.email_pass,
            date=self.today,
            json_location=self.userSettingsJson,
            plotting_mode=False,
        )

        if not result:
            for ID in self.multi_controller.unknownID:
                self.ID_widget.data[ID] = -1
            self.ID_widget.save_json()
        self.ID_widget.connected_Arduino = self.multi_controller.connected_arduinos_HWID
        self.ID_widget.refresh_ui()

    @Slot(Preset)
    def run_handler(self, preset: Preset):
        self.running_preset = preset
        self.trial_queue = preset.trials.copy()

        result = self.multi_controller.initializeMeasurement(
            trial_name=self.trial_name,
            data_dir=self.data_dir,
            email=self.notification_email,
            email_user=self.email_user,
            email_pass=self.email_pass,
            date=self.today,
            json_location=self.userSettingsJson,
            plotting_mode=False,
        )

        if not self.multi_controller.get_valid():
            QMessageBox.warning(self, "Error", "No Arduinos Connected or Initialized.")
            self.running_preset = None  # Abort
            self.trial_queue = []
            return

        if not result:
            # Handle unknown IDs
            custom_print(
                "Initialization failed or found unknown Arduino IDs.",
                self.multi_controller.arduino_ids,
                self.multi_controller.unknownID,
            )
            for ID in self.multi_controller.unknownID:
                self.ID_widget.data[ID] = -1
            self.ID_widget.connected_Arduino = (
                self.multi_controller.connected_arduinos_HWID
            )
            self.ID_widget.save_json()
            self.ID_widget.refresh_ui()
            QMessageBox.warning(
                self,
                "Initialization Warning",
                "Check Arduino assignments. Some IDs are unknown.",
            )
            self.running_preset = None
            self.trial_queue = []
            return
        else:
            # Initialization successful, proceed with first trial
            custom_print(f"Starting {preset.name} with {len(preset.trials)} trials.")
            self.ID_widget.connected_Arduino = (
                self.multi_controller.connected_arduinos_HWID
            )
            self.ID_widget.refresh_ui()
            if self.trial_queue:
                trial = self.trial_queue.pop(0)
                self.running_mode = trial.trial_type
                custom_print(f"Starting trial: {trial}")
                # Use QTimer to ensure init finishes before run_action starts fully
                QTimer.singleShot(
                    0, lambda t=trial: self.run_action(t.trial_type, t.params)
                )
            else:
                QMessageBox.information(self, "Info", "Preset has no trials.")
                self.running_preset = None  # Reset

    @Slot(Trial)
    def start_next_trial(self, trial: Trial):
        self.multi_controller.reset_arduinos()
        self.running_mode = trial.trial_type
        self.run_action(trial.trial_type, trial.params)

    def run_action(self, mode: Mode, params: list[str]):
        custom_print(
            f"Run started for Mode:{Constants.run_modes.get(mode, 'Unknown')}"
        )

        if not self.multi_controller.get_valid():
            QMessageBox.critical(self, "Error", "Lost connection to Arduinos.")
            self.stop_action(Mode.STOP)  # Example: Stop everything
            self.trial_queue = []  # Clear queue
            self.running_preset = None
            self.stop_marquee_timer()
            return

        self.marquee_index = 0
        self.status_bar.showMessage(self.marquee_text)
        self.marquee_timer.start(200)

        self.multi_controller.run(mode, params)

        self.stop_measurement_thread.clear()

    def after_run(self):
        mode = self.running_mode
        if mode in Constants.run_modes:
            self.running_left = False

        custom_print(
            f"Run finished for mode: {Constants.run_modes.get(mode, 'Unknown')}"
        )

        if self.trial_queue:
            trial = self.trial_queue.pop(0)
            custom_print(f"Starting next trial: {trial}")
            QTimer.singleShot(0, lambda t=trial: self.next_trial_signal.emit(t))
        else:
            # Preset finished
            #TODO: why this tiggers every time
            custom_print(f"No trials left, finished {self.running_preset} {self.running_mode}")
            self.running_mode = None
            QTimer.singleShot(0, self.stop_marquee_timer)
            QMessageBox.information(
                self,
                "Notification",
                f"Preset '{self.running_preset.name}' Finished",
            )
            self.running_preset = None

    def load_plotter_dir(self):
        self.plotter_panel.data_location_line_edit.setText(self.multi_controller.trial_dir)

    @Slot()
    def stop_marquee_timer(self):
        self.marquee_timer.stop()
        self.status_bar.clearMessage()

    def stop_action(self, mode: Mode = None):
        custom_print("Stopping Actions")
        self.stop_measurement_thread.set()
        if self.multi_controller is not None:
            self.multi_controller.run(Mode.STOP)

    def on_csv_changed(self, path):
        custom_print(f"CSV file or folder changed: {path}")
        if hasattr(self, "plotter_widget"):
            folder_path = self.data_location_line_edit.text().strip()
            self.plotter_widget.update_plot(folder_path)

    def update_marquee(self):
        """Shifts the text in a circular (marquee) fashion."""
        text_length = len(self.marquee_text)
        # Rotate the text: [index:] + [:index]
        display_text = (
            self.marquee_text[self.marquee_index :]
            + self.marquee_text[: self.marquee_index]
        )
        self.status_bar.showMessage(display_text)

        # Move the index and wrap around
        self.marquee_index = (self.marquee_index - 1) % text_length

    def load_json(self, json_file, to_load):
        """Load JSON data from the specified file and extract the 'arduino_ids' section."""
        try:
            with open(json_file, "r") as f:
                full_data = json.load(f)
            return full_data.get(to_load, {})
        except Exception as e:
            custom_print(f"Error loading JSON: {e}")
            return {}


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
