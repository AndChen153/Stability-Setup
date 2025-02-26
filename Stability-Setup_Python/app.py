# app.py
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QSplitter
)
from PySide6.QtCore import Qt, QFileSystemWatcher

from constants import Mode, Constants
from helper.global_helpers import custom_print
from controller.multi_arduino_controller import MultiController
from gui.plotter_widget import PlotterWidget
from controller import arduino_assignment

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = os.path.join(self.base_dir, "data")
        custom_print(self.base_dir)
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.setWindowTitle("Stability Setup")
        self.setGeometry(100, 100, 1200, 600)

        # Running flags, button dictionaries, textboxes, etc.
        self.running_left = False
        self.running_plotter = False
        self.run_buttons = {}
        self.stop_buttons = {}
        self.textboxes = {}
        self.trial_name = ""  # Initialize shared Trial Name value
        self.trial_name_lineedits = []  # List to hold all Trial Name QLineEdits
        self.notification_email = None
        self.common_param_lineedits = {}

        # CSV watcher, thread control, etc.
        self.csv_watcher = QFileSystemWatcher()
        self.csv_watcher.fileChanged.connect(self.on_csv_changed)
        self.csv_watcher.directoryChanged.connect(self.on_csv_changed)
        self.running_thread = None
        self.stop_measurement_thread = threading.Event()

        self.multi_controller = MultiController()
        self.folder_path = None

        self.estimated_devices = max(1, len(arduino_assignment.get()))

        # File to store presets persistently.
        self.preset_file = os.path.join(os.path.dirname(__file__), "presets.json")

        # Left side: Tab Widget for Scan/MPPT pages.
        self.left_tabs = QTabWidget()
        for mode, page_title in Constants.pages.items():
            if mode == Mode.PLOTTER:
                continue  # skip Plotter on left side
            tab = QWidget()
            self.left_tabs.addTab(tab, page_title)
            self.setup_tab(mode, tab)

        # Right side: Plotter page.
        self.plotter_tab = QWidget()
        self.setup_tab(Mode.PLOTTER, self.plotter_tab)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_tabs)
        splitter.addWidget(self.plotter_tab)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

        # Note: Do not auto-load presets on startup. Defaults come from Constants.

    def setup_tab(self, mode, widget):
        layout = QVBoxLayout(widget)
        form_layout = QFormLayout()
        self.textboxes[mode] = []

        if mode == Mode.PLOTTER:
            # --- Top Controls (CSV Folder Search Box) ---
            line_edit = QLineEdit()
            default = Constants.defaults.get(mode, [""])[0]
            line_edit.setText(default)
            self.data_location_line_edit = line_edit
            self.textboxes[mode].append(("Data Location", line_edit))

            browse_button = QPushButton("Browse...")
            browse_button.clicked.connect(lambda _, le=line_edit: self.open_folder_dialog(le))

            # Container for the CSV folder input and buttons.
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(line_edit)
            h_layout.addWidget(browse_button)

            # Create Plot(s) button.
            run_button = QPushButton("Create Plot(s)")
            run_button.clicked.connect(lambda _, m=mode: self.run_action(m))
            self.run_buttons[mode] = run_button
            h_layout.addWidget(run_button)

            form_layout.addRow("CSV Folder", container)
            layout.addLayout(form_layout)

            # --- Plot Container (for the plot tabs) ---
            # Create a dedicated container for the plot widgets that will appear below the controls.
            self.plot_container = QWidget()
            self.plot_container.setLayout(QVBoxLayout())
            layout.addWidget(self.plot_container)
        else:
            if mode in Constants.params:
                params = Constants.params[mode]
                defaults = Constants.defaults.get(mode, [""] * len(params))
                for param, default in zip(params, defaults):
                    if param == Constants.timeParam:
                        # Create a container widget for the unit buttons and textbox
                        container = QWidget()
                        h_layout = QHBoxLayout(container)
                        h_layout.setContentsMargins(0, 0, 0, 0)

                        # Create unit toggle buttons
                        mins_button = QPushButton("Mins")
                        hrs_button = QPushButton("Hrs")
                        # Create the QLineEdit for time value
                        time_line_edit = QLineEdit()
                        time_line_edit.setText(default)

                        h_layout.addWidget(mins_button)
                        h_layout.addWidget(hrs_button)
                        h_layout.addWidget(time_line_edit)

                        # Set default unit state to minutes.
                        self.mppt_time_unit = "mins"
                        self.mppt_time_line_edit = time_line_edit
                        self.mppt_mins_button = mins_button
                        self.mppt_hrs_button = hrs_button

                        # Disable the Mins button since that is the active unit
                        mins_button.setEnabled(False)

                        # Connect button signals to switch units
                        mins_button.clicked.connect(self.switch_to_minutes)
                        hrs_button.clicked.connect(self.switch_to_hours)
                        time_line_edit.textChanged.connect(self.update_estimated_data_amount)

                        form_layout.addRow(param, container)
                        # Store the QLineEdit (not the container) so that other functions work as before.
                        self.textboxes[mode].append((param, time_line_edit))
                    else:
                        line_edit = QLineEdit()
                        line_edit.setText(default)
                        if param in Constants.common_params:
                            if param not in self.common_param_lineedits:
                                self.common_param_lineedits[param] = []
                            self.common_param_lineedits[param].append(line_edit)
                            line_edit.textChanged.connect(lambda text, p=param, src=line_edit: self.on_common_param_changed(p, text, src))
                        # For other parameters (including those with no special behavior)
                        form_layout.addRow(param, line_edit)
                        self.textboxes[mode].append((param, line_edit))


                # For MPPT mode, add the estimated data amount textbox.
                if mode == Mode.MPPT:
                    self.mppt_estimated_gb = QLineEdit()
                    self.mppt_estimated_gb.setReadOnly(True)
                    self.mppt_estimated_gb.setText("0.0")  # initial value
                    self.update_estimated_data_amount()
                    form_layout.addRow("Estimated Data Amount", self.mppt_estimated_gb)
                    # self.textboxes[mode].append(("Estimated Data Amount", self.mppt_estimated_gb))
            else:
                form_layout.addRow(QLabel("No parameters defined for this mode."))
        layout.addLayout(form_layout)

        if mode != Mode.PLOTTER:
            # Left column: Preset buttons.
            preset_container = QWidget()
            preset_layout = QHBoxLayout(preset_container)
            preset_layout.setContentsMargins(0, 0, 0, 0)
            save_button = QPushButton("Save Preset")
            save_button.clicked.connect(lambda _, m=mode: self.save_preset_action(m))
            preset_layout.addWidget(save_button)
            load_button = QPushButton("Load Preset")
            load_button.clicked.connect(lambda _, m=mode: self.load_preset_action(m))
            preset_layout.addWidget(load_button)

            # Right column: Stop and Run buttons.
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 0, 0, 0)
            stop_button = QPushButton("Stop")
            stop_button.clicked.connect(lambda _, m=mode: self.stop_action(m))
            button_layout.addWidget(stop_button)
            self.stop_buttons[mode] = stop_button
            run_button = QPushButton("Run")
            run_button.clicked.connect(lambda _, m=mode: self.run_action(m))
            button_layout.addWidget(run_button)
            self.run_buttons[mode] = run_button

            form_layout.addRow(preset_container, button_container)

        # layout.addLayout(form_layout)

        if mode == Mode.PLOTTER:
            self.plotter_widget = PlotterWidget()
            layout.addWidget(self.plotter_widget)

        self.update_buttons()

    def update_estimated_data_amount(self):
        time_text = None
        delay_text = None
        for param, textbox in self.textboxes.get(Mode.MPPT, []):
            if param == Constants.timeParam:
                time_text = textbox.text()
            elif param == "Measurement Delay (ms)":
                delay_text = textbox.text()
        try:
            # Convert to seconds based on the current unit
            if self.mppt_time_unit == "hrs":
                Time_s = float(time_text) * 3600 if time_text else 0.0
            else:
                Time_s = float(time_text) * 60 if time_text else 0.0
            Delay_s = float(delay_text) / 1000 if delay_text else 0.0
            if Delay_s == 0:
                estimated = 0.0
            else:
                estimated = self.estimated_devices * (Constants.kbPerDataPoint * Time_s / (Delay_s + 0.1))

            unit = "kb"
            if estimated > 1000000:
                estimated = estimated / 1000000
                unit = "gb"
            elif estimated > 1000:
                estimated = estimated / 1000
                unit = "mb"

            estimated = round(estimated, 2)
            self.mppt_estimated_gb.setText(f"{str(estimated)} {unit}")
        except ValueError:
            self.mppt_estimated_gb.setText("Error")

    def switch_to_minutes(self):
        if self.mppt_time_unit == "mins":
            return
        try:
            current_value = float(self.mppt_time_line_edit.text())
            # Converting from hours to minutes:
            new_value = current_value * 60
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "mins"
            # Update button states:
            self.mppt_mins_button.setEnabled(False)
            self.mppt_hrs_button.setEnabled(True)
            self.update_estimated_data_amount()
        except ValueError:
            pass

    def switch_to_hours(self):
        if self.mppt_time_unit == "hrs":
            return
        try:
            current_value = float(self.mppt_time_line_edit.text())
            # Converting from minutes to hours:
            new_value = current_value / 60
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "hrs"
            self.mppt_hrs_button.setEnabled(False)
            self.mppt_mins_button.setEnabled(True)
            self.update_estimated_data_amount()
        except ValueError:
            pass


    def on_common_param_changed(self, param, text, source):
        """
        When a common parameter's text changes, update all QLineEdits associated
        with that parameter (except the source that triggered the change).
        """
        for widget in self.common_param_lineedits.get(param, []):
            if widget is not source:
                widget.blockSignals(True)
                widget.setText(text)
                widget.blockSignals(False)

    def update_buttons(self):
        # Update button states based on running flags.
        for mode in self.run_buttons:
            if mode == Mode.PLOTTER:
                self.run_buttons[mode].setEnabled(True)
            else:
                self.run_buttons[mode].setEnabled(not self.running_left)
        for mode in self.stop_buttons:
            self.stop_buttons[mode].setEnabled(self.running_left)

    def open_folder_dialog(self, line_edit: QLineEdit):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select CSV Folder",
            ""
        )
        if folder_path:
            line_edit.setText(folder_path)

    def run_action(self, mode: Mode):
        custom_print(f"Run button clicked on page: {Constants.pages.get(mode, 'Unknown')}")
        if mode == Mode.PLOTTER:
            self.running_plotter = True
            folder_path = self.data_location_line_edit.text().strip()
            if os.path.isdir(folder_path):
                plot_groups = self.getPlotGroups(folder_path)
                self.update_plot_tabs(plot_groups)
            else:
                custom_print("Invalid folder.")
        elif mode in [Mode.SCAN, Mode.MPPT]:
            self.running_left = True
            self.update_buttons()

            values = []
            for param, textbox in self.textboxes.get(mode, []):
                if param == "Trial Name":
                    self.trial_name = textbox.text()
                elif param == "Email for Notification":
                    self.notification_email = textbox.text()

                if param == Constants.timeParam:
                    time_text = textbox.text()
                    if self.mppt_time_unit == "hrs":
                        Time_m = int(time_text) * 60 if time_text else 0.0
                    else:
                        Time_m = int(time_text) if time_text else 0.0
                    values.append(str(Time_m))
                else:
                    values.append(textbox.text())

            self.multi_controller.initializeMeasurement(
                trial_name=self.trial_name,
                data_dir=self.data_dir,
                email=self.notification_email,
                date=self.today,
                plotting_mode=False)
            self.data_location_line_edit.setText(self.multi_controller.trial_dir)
            self.multi_controller.run(mode, values)
            self.left_tabs.tabBar().setEnabled(False)

            # Start a thread to monitor the run process.
            self.stop_measurement_thread.clear()
            thread = threading.Thread(
                target=self.wait_for_run_finish, args=([mode]), daemon=True
            )
            self.running_thread = thread
            thread.start()

    def wait_for_run_finish(self, mode):
        if mode != Mode.PLOTTER:
            while not self.stop_measurement_thread.is_set() and self.multi_controller.active_threads:
                threading.Event().wait(0.1)
        self.after_run(mode)

    def after_run(self, mode: Mode):
        self.running_left = False
        self.update_buttons()
        self.left_tabs.tabBar().setEnabled(True)
        while self.multi_controller.controllers:
            threading.Event().wait(0.1)
        self.multi_controller.controllers = {}
        custom_print(f"Run finished on page: {Constants.pages.get(mode, 'Unknown')}")

    def stop_action(self, mode: Mode):
        custom_print(f"Stop button clicked on page: {Constants.pages.get(mode, 'Unknown')}")
        self.stop_measurement_thread.set()
        if self.multi_controller is not None:
            self.multi_controller.run(Mode.STOP)
        self.running_left = False
        self.update_buttons()
        self.left_tabs.tabBar().setEnabled(True)

    def on_csv_changed(self, path):
        custom_print(f"CSV file or folder changed: {path}")
        if hasattr(self, 'plotter_widget'):
            folder_path = self.data_location_line_edit.text().strip()
            self.plotter_widget.update_plot(folder_path)

    def save_preset_action(self, mode: Mode):
        """
        Gather current parameters for the given mode and save them
        to a JSON file so they can be loaded later.
        """
        presets = {}
        if os.path.exists(self.preset_file):
            with open(self.preset_file, 'r') as f:
                try:
                    presets = json.load(f)
                except json.JSONDecodeError:
                    presets = {}

        preset_for_mode = {}
        for param, textbox in self.textboxes.get(mode, []):
            preset_for_mode[param] = textbox.text()

        presets[mode.name] = preset_for_mode

        with open(self.preset_file, 'w') as f:
            json.dump(presets, f, indent=4)
        custom_print(f"Presets saved for {Constants.pages.get(mode, 'Unknown')} mode.")

    def load_preset_action(self, mode: Mode):
        """
        Load presets for the given mode from the JSON file and update the text boxes.
        """
        if not os.path.exists(self.preset_file):
            custom_print("No presets file found.")
            return

        with open(self.preset_file, 'r') as f:
            try:
                presets = json.load(f)
            except json.JSONDecodeError:
                custom_print("Error loading presets: JSON decode error.")
                return

        mode_key = mode.name
        if mode_key in presets:
            for param, textbox in self.textboxes.get(mode, []):
                if param in presets[mode_key]:
                    textbox.setText(presets[mode_key][param])
            custom_print(f"Presets loaded for {Constants.pages.get(mode, 'Unknown')} mode.")
        else:
            custom_print(f"No presets saved for {Constants.pages.get(mode, 'Unknown')} mode.")

        self.update_estimated_data_amount()

    def update_plot_tabs(self, plot_groups):
        # Get the layout of the plot container.
        plot_layout = self.plot_container.layout()

        # Clear any existing plot widgets.
        while plot_layout.count():
            child = plot_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create a new QTabWidget to hold individual plot tabs.
        plot_tab_widget = QTabWidget()

        # For each plot group, create a new PlotterWidget, update it with filepaths, and add it as a tab.
        for title, filepaths in plot_groups.items():
            plotter_widget = PlotterWidget()
            # Make sure your PlotterWidget.update_plot can handle a list of filepaths.
            plotter_widget.update_plot(title, filepaths)
            plot_tab_widget.addTab(plotter_widget, title)

        # Add the QTabWidget to the dedicated plot container.
        plot_layout.addWidget(plot_tab_widget)

    def getPlotGroups(self, folder_path):
        csv_files = sorted(
            [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(".csv")
            ]
        )
        file_groups_dict = {}
        for file in csv_files:
            head, tail = os.path.split(file)
            params = tail.split("__")
            filetype = params[-1].split(".")[0]  # get scan or mppt from scan.csv
            if "ID" not in params[1]:
                test_name = params[1]
            else:
                test_name = ""

            name_parts = [val for val in [test_name, params[0], filetype] if val]

            plot_name = " ".join(name_parts)
            if plot_name in file_groups_dict:
                file_groups_dict[plot_name].append(file)
            else:
                file_groups_dict[plot_name] = [file]

        return file_groups_dict


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
