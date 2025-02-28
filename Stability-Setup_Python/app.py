# app.py
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QSplitter,
    QComboBox,
    QSystemTrayIcon,
    QMessageBox,
    QStatusBar,
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QTimer

from constants import Mode, Constants
from helper.global_helpers import custom_print
from controller.multi_arduino_controller import MultiController
from gui.plotter_widget import PlotterWidget
from gui.id_widget import IDWidget
from gui.warning_popup import SelectionPopup, ContinuePopup
from controller import arduino_assignment


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = os.path.join(self.base_dir, "data")
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
        # Change the preset structure so that each mode stores a dictionary of presets keyed by trial name.
        self.arduino_assignment_json = os.path.join(
            os.path.dirname(__file__), "arduino_ids.json"
        )
        self.ID_widget = IDWidget(self.arduino_assignment_json)
        self.ID_widget.refreshRequested.connect(self.initializeArduinoConnections)

        # Dictionary to hold the QComboBox for presets for each mode.
        self.preset_dropdown = {}

        # Left side: Tab Widget for Scan/MPPT pages.
        self.left_tabs = QTabWidget()
        for mode, page_title in Constants.pages.items():
            if mode in Constants.right_modes:
                continue  # skip Plotter on left side
            tab = QWidget()
            self.left_tabs.addTab(tab, page_title)
            self.setup_tab(mode, tab)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.addWidget(self.left_tabs)
        left_layout.addWidget(self.ID_widget)

        # Right side: Plotter page.
        self.plotter_tab = QWidget()
        self.setup_tab(Mode.PLOTTER, self.plotter_tab)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.plotter_tab)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Prepare marquee animation
        self.marquee_timer = QTimer(self)
        self.marquee_timer.timeout.connect(self.update_marquee)

        # The text to animate (leading/trailing spaces can help the effect)
        self.marquee_text = "  Running...  "
        self.marquee_index = 0

        self.initializeArduinoConnections()

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
            browse_button.clicked.connect(
                lambda _, le=line_edit: self.open_folder_dialog(le)
            )

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
            self.plot_container = QWidget()
            self.plot_container.setLayout(QVBoxLayout())
            layout.addWidget(self.plot_container)
        else:
            # Left column: Preset dropdown and Save button.
            preset_container = QWidget()
            preset_layout = QHBoxLayout(preset_container)
            preset_layout.setContentsMargins(0, 0, 0, 0)

            # Create dropdown for presets.
            self.preset_dropdown[mode] = QComboBox()
            self.preset_dropdown[mode].addItem("Select Preset")
            self.preset_dropdown[mode].setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )
            self.preset_dropdown[mode].setMinimumContentsLength(10)
            self.preset_dropdown[mode].currentIndexChanged.connect(
                lambda index, m=mode: self.preset_selected(m)
            )
            preset_layout.addWidget(self.preset_dropdown[mode])

            save_button = QPushButton("Save Preset")
            save_button.setMaximumWidth(150)
            save_button.clicked.connect(lambda _, m=mode: self.save_preset_action(m))
            preset_layout.addWidget(save_button)

            delete_button = QPushButton("Delete Preset")
            delete_button.setMaximumWidth(150)
            delete_button.clicked.connect(
                lambda _, m=mode: self.delete_preset_action(m)
            )
            preset_layout.addWidget(delete_button)
            form_layout.addRow(preset_container)

            if mode in Constants.params:
                params = Constants.common_params + Constants.params[mode]
                defaults = Constants.common_defaults + Constants.defaults.get(
                    mode, [""] * len(params)
                )
                for param, default in zip(params, defaults):
                    if param == Constants.timeParam:
                        container = QWidget()
                        h_layout = QHBoxLayout(container)
                        h_layout.setContentsMargins(0, 0, 0, 0)

                        mins_button = QPushButton("Mins")
                        hrs_button = QPushButton("Hrs")
                        time_line_edit = QLineEdit()
                        time_line_edit.setText(default)

                        h_layout.addWidget(mins_button)
                        h_layout.addWidget(hrs_button)
                        h_layout.addWidget(time_line_edit)

                        self.mppt_time_unit = "mins"
                        self.mppt_time_line_edit = time_line_edit
                        self.mppt_mins_button = mins_button
                        self.mppt_hrs_button = hrs_button

                        mins_button.setEnabled(False)

                        mins_button.clicked.connect(self.switch_to_minutes)
                        hrs_button.clicked.connect(self.switch_to_hours)
                        time_line_edit.textChanged.connect(
                            self.update_estimated_data_amount
                        )

                        form_layout.addRow(param, container)
                        self.textboxes[mode].append((param, time_line_edit))
                    elif mode == Mode.SCAN and param == "Scan Mode":
                        toggle_button = QPushButton()
                        toggle_button.setCheckable(True)
                        # Set the default value (if the default string is "dark", set accordingly)
                        if default.lower() == "dark":
                            toggle_button.setText("dark")
                            toggle_button.setChecked(True)
                        else:
                            toggle_button.setText("light")
                            toggle_button.setChecked(False)
                        # Connect the button to a toggle handler
                        toggle_button.clicked.connect(
                            lambda _, btn=toggle_button: self.toggle_scan_mode(btn)
                        )
                        form_layout.addRow(param, toggle_button)
                        self.textboxes[mode].append((param, toggle_button))
                    else:
                        line_edit = QLineEdit()
                        line_edit.setText(default)
                        if param in Constants.common_params:
                            if param not in self.common_param_lineedits:
                                self.common_param_lineedits[param] = []
                            self.common_param_lineedits[param].append(line_edit)
                            line_edit.textChanged.connect(
                                lambda text, p=param, src=line_edit: self.on_common_param_changed(
                                    p, text, src
                                )
                            )
                        form_layout.addRow(param, line_edit)
                        self.textboxes[mode].append((param, line_edit))

                if mode == Mode.MPPT:
                    self.mppt_estimated_gb = QLineEdit()
                    self.mppt_estimated_gb.setReadOnly(True)
                    self.mppt_estimated_gb.setText("0.0")
                    self.mppt_estimated_gb.setText("0.0")
                    self.mppt_estimated_gb.setStyleSheet(
                        "QLineEdit { border: none; background-color: transparent; }"
                    )
                    self.update_estimated_data_amount()
                    form_layout.addRow("Estimated Data Amount", self.mppt_estimated_gb)
            else:
                form_layout.addRow(QLabel("No parameters defined for this mode."))
            layout.addLayout(form_layout)

        if mode not in [Mode.PLOTTER]:

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
            form_layout.addRow(QWidget(), button_container)
            # Populate the dropdown with any previously saved presets.
            self.populate_preset_dropdown(mode)

        layout.addLayout(form_layout)

        self.update_buttons()

    def initializeArduinoConnections(self):
        custom_print("Called Initilalize Arduino COnnection")
        result = self.multi_controller.initializeMeasurement(
            trial_name=self.trial_name,
            data_dir=self.data_dir,
            email=self.notification_email,
            date=self.today,
            json_location=self.arduino_assignment_json,
            plotting_mode=False,
        )

        if not result:
            for ID in self.multi_controller.unknownID:
                self.ID_widget.data[ID] = -1
            self.ID_widget.save_json()
        self.ID_widget.connected_Arduino = self.multi_controller.connected_arduinos_HWID
        self.ID_widget.refresh_ui()

    def update_estimated_data_amount(self):
        time_text = None
        delay_text = None
        for param, textbox in self.textboxes.get(Mode.MPPT, []):
            if param == Constants.timeParam:
                time_text = textbox.text()
            elif param == "Measurement Delay (ms)":
                delay_text = textbox.text()
        try:
            if self.mppt_time_unit == "hrs":
                Time_s = float(time_text) * 3600 if time_text else 0.0
            else:
                Time_s = float(time_text) * 60 if time_text else 0.0
            Delay_s = float(delay_text) / 1000 if delay_text else 0.0
            if Delay_s == 0:
                estimated = 0.0
            else:
                estimated = self.estimated_devices * (
                    Constants.kbPerDataPoint * Time_s / (Delay_s + 0.1)
                )

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
            new_value = current_value * 60
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "mins"
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
            new_value = current_value / 60
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "hrs"
            self.mppt_hrs_button.setEnabled(False)
            self.mppt_mins_button.setEnabled(True)
            self.update_estimated_data_amount()
        except ValueError:
            pass

    def on_common_param_changed(self, param, text, source):
        for widget in self.common_param_lineedits.get(param, []):
            if widget is not source:
                widget.blockSignals(True)
                widget.setText(text)
                widget.blockSignals(False)

    def update_buttons(self):
        for mode in self.run_buttons:
            if mode == Mode.PLOTTER:
                self.run_buttons[mode].setEnabled(True)
            else:
                self.run_buttons[mode].setEnabled(not self.running_left)
        for mode in self.stop_buttons:
            self.stop_buttons[mode].setEnabled(self.running_left)

    def open_folder_dialog(self, line_edit: QLineEdit):
        folder_path = QFileDialog.getExistingDirectory(self, "Select CSV Folder", "")
        if folder_path:
            line_edit.setText(folder_path)

    def run_action(self, mode: Mode):
        custom_print(
            f"Run button clicked on page: {Constants.pages.get(mode, 'Unknown')}"
        )
        if mode == Mode.PLOTTER:
            self.running_plotter = True
            folder_path = self.data_location_line_edit.text().strip()
            if os.path.isdir(folder_path):
                plot_groups = self.getPlotGroups(folder_path)
                self.update_plot_tabs(plot_groups)
            else:
                continue_popup = ContinuePopup(
                    parent=self, title="Error", message="Invalid Plotting Folder"
                )
                continue_popup.exec_()

            self.after_run(mode)

        elif mode in [Mode.SCAN, Mode.MPPT]:
            params = []
            for param, textbox in self.textboxes.get(mode, []):
                if param == "Trial Name":
                    self.trial_name = textbox.text()
                elif param == "Email for Notification":
                    self.notification_email = textbox.text()
                else:
                    if param == Constants.timeParam:
                        time_text = textbox.text()
                        if self.mppt_time_unit == "hrs":
                            Time_m = int(time_text) * 60 if time_text else 0.0
                        else:
                            Time_m = int(time_text) if time_text else 0.0
                        params.append(str(Time_m))
                    else:
                        params.append(textbox.text())

            range_popup = SelectionPopup(
                parent=self, title="Range Warning", current_values=params, mode=mode
            )

            if not range_popup.exec_():
                return

            result = self.multi_controller.initializeMeasurement(
                trial_name=self.trial_name,
                data_dir=self.data_dir,
                email=self.notification_email,
                date=self.today,
                json_location=self.arduino_assignment_json,
                plotting_mode=False,
            )

            if not self.multi_controller.get_valid():
                continue_popup = ContinuePopup(
                    parent=self, title="Error", message="No Arduinos Connected"
                )
                continue_popup.exec_()
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
                self.update_buttons()
                self.data_location_line_edit.setText(self.multi_controller.trial_dir)
                self.multi_controller.run(mode, params)
                self.left_tabs.tabBar().setEnabled(False)

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
        self.running_left = False
        self.update_buttons()
        self.marquee_timer.stop()
        self.status_bar.clearMessage()
        self.left_tabs.tabBar().setEnabled(True)

        if mode in Constants.left_modes:
            while self.multi_controller.controllers:
                threading.Event().wait(0.1)
            self.multi_controller.controllers = {}
        custom_print(f"Run finished on page: {Constants.pages.get(mode, 'Unknown')}")

    def stop_action(self, mode: Mode):
        custom_print(
            f"Stop button clicked on page: {Constants.pages.get(mode, 'Unknown')}"
        )
        self.stop_measurement_thread.set()
        if self.multi_controller is not None:
            self.multi_controller.run(Mode.STOP)
        self.running_left = False
        self.update_buttons()
        self.left_tabs.tabBar().setEnabled(True)

    def save_preset_action(self, mode: Mode):
        # Get trial name from the corresponding textbox.
        trial_name = None
        for param, textbox in self.textboxes.get(mode, []):
            if param == "Trial Name":
                trial_name = textbox.text().strip()
                break
        if not trial_name:
            self.show_popup("Trial Name is required to save a preset.")
            return

        if os.path.exists(self.preset_file):
            with open(self.preset_file, "r") as f:
                try:
                    presets = json.load(f)
                except json.JSONDecodeError:
                    presets = {}
        else:
            presets = {}

        preset_for_mode = {}
        for param, textbox in self.textboxes.get(mode, []):
            preset_for_mode[param] = textbox.text()
        if mode.name not in presets:
            presets[mode.name] = {}
        presets[mode.name][trial_name] = preset_for_mode

        with open(self.preset_file, "w") as f:
            json.dump(presets, f, indent=4)
        custom_print(
            f"Preset '{trial_name}' saved for {Constants.pages.get(mode, 'Unknown')} mode."
        )

        # Update the dropdown with the new preset.
        self.populate_preset_dropdown(mode)

    def delete_preset_action(self, mode: Mode):
        # Get trial name from the corresponding textbox.
        trial_name = None
        for param, textbox in self.textboxes.get(mode, []):
            if param == "Trial Name":
                trial_name = textbox.text().strip()
                break
        if not trial_name:
            self.show_popup("Trial Name is required to delete a preset.")
            return

        if os.path.exists(self.preset_file):
            with open(self.preset_file, "r") as f:
                try:
                    presets = json.load(f)
                except json.JSONDecodeError:
                    presets = {}
        else:
            presets = {}

        if presets[mode.name][trial_name]:
            del presets[mode.name][trial_name]

        with open(self.preset_file, "w") as f:
            json.dump(presets, f, indent=4)
        custom_print(
            f"Preset '{trial_name}' deleted for {Constants.pages.get(mode, 'Unknown')} mode."
        )

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.show()

        # Later, when you want to display a notification:
        self.tray_icon.showMessage("Notification Title", "This is a tray message")
        # Update the dropdown with the new preset.
        self.populate_preset_dropdown(mode)

    def populate_preset_dropdown(self, mode: Mode):
        if os.path.exists(self.preset_file):
            with open(self.preset_file, "r") as f:
                try:
                    presets = json.load(f)
                except json.JSONDecodeError:
                    presets = {}
        else:
            presets = {}
        presets_for_mode = presets.get(mode.name, {})
        dropdown = self.preset_dropdown.get(mode)
        if dropdown is not None:
            dropdown.blockSignals(True)
            dropdown.clear()
            dropdown.addItem("Select Preset")
            for trial_name in presets_for_mode.keys():
                dropdown.addItem(trial_name)
            dropdown.blockSignals(False)

    def preset_selected(self, mode: Mode):
        dropdown = self.preset_dropdown.get(mode)
        if dropdown:
            trial_name = dropdown.currentText()
            if trial_name == "Select Preset":
                return
            if os.path.exists(self.preset_file):
                with open(self.preset_file, "r") as f:
                    try:
                        presets = json.load(f)
                    except json.JSONDecodeError:
                        presets = {}
            else:
                presets = {}
            presets_for_mode = presets.get(mode.name, {})
            preset = presets_for_mode.get(trial_name)
            if preset:
                for param, textbox in self.textboxes.get(mode, []):
                    if param in preset:
                        textbox.setText(preset[param])
                custom_print(
                    f"Preset '{trial_name}' loaded for {Constants.pages.get(mode, 'Unknown')} mode."
                )

    def update_plot_tabs(self, plot_groups):
        plot_layout = self.plot_container.layout()
        while plot_layout.count():
            child = plot_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        plot_tab_widget = QTabWidget()
        for title, filepaths in plot_groups.items():
            plotter_widget = PlotterWidget()
            plotter_widget.update_plot(title, filepaths)
            plot_tab_widget.addTab(plotter_widget, title)
        plot_layout.addWidget(plot_tab_widget)

    def on_csv_changed(self, path):
        custom_print(f"CSV file or folder changed: {path}")
        if hasattr(self, "plotter_widget"):
            folder_path = self.data_location_line_edit.text().strip()
            self.plotter_widget.update_plot(folder_path)

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
            filetype = params[-1].split(".")[0]
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

    def save_arduino_ids(self, json_file):
        new_ids = {}
        for id_str, line_edit in self.arduino_id_lineedits.items():
            try:
                new_ids[id_str] = int(line_edit.text())
            except ValueError:
                new_ids[id_str] = line_edit.text()
        with open(json_file, "w") as f:
            json.dump(new_ids, f, indent=4)
        custom_print("Arduino IDs updated and saved.")

    def show_popup(self, message: str):
        QMessageBox.information(self, "Notification", message)

    def update_marquee(self):
        """Shifts the text in a circular (marquee) fashion."""
        text_length = len(self.marquee_text)
        # Rotate the text: [index:] + [:index]
        display_text = (self.marquee_text[self.marquee_index:] +
                        self.marquee_text[:self.marquee_index])
        self.status_bar.showMessage(display_text)

        # Move the index and wrap around
        self.marquee_index = (self.marquee_index - 1) % text_length

    def toggle_scan_mode(self, btn: QPushButton):
        # Toggle the text and check state between "light" and "dark"
        if btn.text().lower() == "light":
            btn.setText("dark")
            btn.setChecked(True)
        else:
            btn.setText("light")
            btn.setChecked(False)


if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
