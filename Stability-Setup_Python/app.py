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
    QStyleFactory
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor
import assets_rc

from constants import Mode, Constants
from helper.global_helpers import custom_print
from controller.multi_arduino_controller import MultiController
from gui.arduino_manager.id_widget import IDWidget
from gui.results_viewer.plotter_panel import PlotterPanel
from gui.trial_manager.setup_tabs import SetupTabs
from gui.trial_manager.preset_window_widget import PresetQueueWidget
from gui.trial_manager.preset_loader import PresetManager
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

class MainWindow(QMainWindow):
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
        self.tab_components = {}

        # Email
        self.notification_email = None
        self.email_user = self.load_json(self.userSettingsJson, "email_settings")[
            "user"
        ]
        self.email_pass = self.load_json(self.userSettingsJson, "email_settings")[
            "pass"
        ]

        # CSV watcher, thread control, etc.
        self.csv_watcher = QFileSystemWatcher()
        self.csv_watcher.fileChanged.connect(self.on_csv_changed)
        self.csv_watcher.directoryChanged.connect(self.on_csv_changed)
        self.running_thread = None
        self.stop_measurement_thread = threading.Event()

        self.multi_controller = MultiController()
        self.folder_path = None
        self.estimated_devices = max(1, len(arduino_assignment.get()))
        self.toggle_button = None

        self.ID_widget = IDWidget(self.userSettingsJson)
        self.ID_widget.refreshRequested.connect(self.initializeArduinoConnections)

        self.setup_tabs = SetupTabs(
            self.tab_components,
            self.textboxes,
        )

        # Connect each SetupTab's signals to the MainWindow's action handlers.
        self.setup_tabs.connect_signals(self.run_action, self.stop_action)

        self.preset_queue = PresetQueueWidget()

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.preset_queue)
        self.splitter.addWidget(self.setup_tabs)

        self.preset_manager = PresetManager(
            self.userSettingsJson
        )

        self.plotter_panel = PlotterPanel(
            default_folder=Constants.defaults.get(Mode.PLOTTER, [""])[0]
        )

        tabs = QTabWidget()
        tabs.addTab(self.splitter, Constants.trial_manager)
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

    def run_action(self, mode: Mode):
        custom_print(
            f"Run button clicked on page: {Constants.run_modes.get(mode, 'Unknown')}"
        )
        params = []
        for param, textbox in self.textboxes.get(mode, []):
            if param == "Trial Name":
                self.trial_name = textbox.text()
            elif param == "Email for Notification":
                self.notification_email = textbox.text()
            else:
                if param == Constants.time_param:
                    time_text = textbox.text()
                    if self.mppt_time_unit == "hrs":
                        Time_m = int(float(time_text)) * 60 if time_text else 0.0
                    else:
                        Time_m = int(float(time_text)) if time_text else 0.0
                    params.append(str(Time_m))
                elif param == Constants.scan_mode_param:
                    # TODO: Fix toggle button connection for light
                    # if self.toggle_button.isChecked():
                    #     params.append("0")
                    # else:
                    #     params.append("1")
                    params.append("1")
                else:
                    params.append(textbox.text())

        custom_print(params)

        range_popup = SelectionPopup(
            parent=self, title="Range Warning", current_values=params, mode=mode
        )

        if not range_popup.exec_():
            return

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
            QMessageBox.information(self, "Error", "No Arduinos Connected.")
            return

        if not result:
            custom_print(
                self.multi_controller.arduino_ids, self.multi_controller.unknownID
            )
            for ID in self.multi_controller.unknownID:
                self.ID_widget.data[ID] = -1
            custom_print(list(self.multi_controller.arduino_ids.keys()))
            self.ID_widget.connected_Arduino = (
                self.multi_controller.connected_arduinos_HWID
            )
            self.ID_widget.save_json()
            self.ID_widget.refresh_ui()
        else:
            self.marquee_index = 0
            self.status_bar.showMessage(self.marquee_text)
            self.marquee_timer.start(200)

            self.running_left = True
            self.tab_components[mode].update_buttons()
            # TODO: fix the auto population
            # self.data_location_line_edit.setText(self.multi_controller.trial_dir)
            self.multi_controller.run(mode, params)
            self.setup_tabs.set_tab_bar(False)

            self.stop_measurement_thread.clear()
            thread = threading.Thread(
                target=self.wait_for_run_finish, args=([mode]), daemon=True
            )
            self.running_thread = thread
            thread.start()

    def wait_for_run_finish(self, mode):
        if mode != Mode.PLOTTER:
            while (
                not self.stop_measurement_thread.is_set()
                and self.multi_controller.active_threads
            ):
                threading.Event().wait(0.1)
        self.after_run(mode)

    def after_run(self, mode: Mode):
        if mode in Constants.run_modes:
            self.running_left = False
            self.tab_components[mode].update_buttons()
            self.marquee_timer.stop()
            self.status_bar.clearMessage()
            self.setup_tabs.set_tab_bar(True)
            while self.multi_controller.controllers:
                threading.Event().wait(0.1)
            self.multi_controller.controllers = {}

        QMessageBox.information(
            self,
            "Notification",
            f"{Constants.run_modes.get(mode, 'Unknown')} Trial Finished",
        )

        custom_print(
            f"Run finished on page: {Constants.run_modes.get(mode, 'Unknown')}"
        )

    def stop_action(self, mode: Mode):
        custom_print(
            f"Stop button clicked on page: {Constants.run_modes.get(mode, 'Unknown')}"
        )
        self.stop_measurement_thread.set()
        if self.multi_controller is not None:
            self.multi_controller.run(Mode.STOP)
        self.running_left = False
        self.tab_components[mode].update_buttons()
        self.setup_tabs.set_tab_bar(True)

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
    app.setStyle(QStyleFactory.create('Fusion'))
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
    window.setWindowIcon(QIcon( ":/icons/logo.png"))
    window.setWindowTitle("Stability Measurement System")
    window.show()
    sys.exit(app.exec())
