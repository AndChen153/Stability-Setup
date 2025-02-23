#app.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QSplitter
)
from PySide6.QtCore import Qt, QFileSystemWatcher
import threading
import os
from datetime import datetime
from constants import Mode, Constants
from helper.global_helpers import custom_print
from controller.multi_arduino_controller import MultiController
from gui.plotter_widget import PlotterWidget


# TODO fix SingleController not properly exiting
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.setWindowTitle("Stability Setup")
        self.setGeometry(100, 100, 1200, 600)

        # Running flags, button dictionaries, textboxes, etc.
        self.running_left = False
        self.running_plotter = False
        self.run_buttons = {}
        self.stop_buttons = {}
        self.textboxes = {}
        self.trial_name = None

        # CSV watcher, thread control, etc.
        self.csv_watcher = QFileSystemWatcher()
        self.csv_watcher.fileChanged.connect(self.on_csv_changed)
        self.csv_watcher.directoryChanged.connect(self.on_csv_changed)
        self.running_thread = None
        self.stop_measurement_thread = threading.Event()

        self.multi_controller = None
        self.folder_path = None

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

    def setup_tab(self, mode, widget):
        layout = QVBoxLayout(widget)
        form_layout = QFormLayout()
        self.textboxes[mode] = []

        # For the Plotter page, we just want a CSV folder selector...
        if mode == Mode.PLOTTER:
            # Create a QLineEdit to hold the folder path.
            line_edit = QLineEdit()
            default = Constants.defaults.get(mode, [""])[0]
            line_edit.setText(default)
            self.data_location_line_edit = line_edit
            self.textboxes[mode].append(("Data Location", line_edit))

            browse_button = QPushButton("Browse...")
            browse_button.clicked.connect(
                lambda _, le=line_edit: self.open_folder_dialog(le)
            )
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(line_edit)
            h_layout.addWidget(browse_button)
            form_layout.addRow("CSV Folder", container)
        else:
            # For the other modes, add parameters as before.
            if mode in Constants.params:
                params = Constants.params[mode]
                defaults = Constants.defaults.get(mode, [""] * len(params))
                for param, default in zip(params, defaults):
                    line_edit = QLineEdit()
                    line_edit.setText(default)
                    form_layout.addRow(param, line_edit)
                    self.textboxes[mode].append((param, line_edit))
            else:
                form_layout.addRow(QLabel("No parameters defined for this mode."))

        # Add the run (and if needed, stop) buttons.
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        if mode != Mode.PLOTTER:
            stop_button = QPushButton("Stop")
            stop_button.clicked.connect(lambda _, m=mode: self.stop_action(m))
            button_layout.addWidget(stop_button)
            self.stop_buttons[mode] = stop_button
            run_button = QPushButton("Run")
        else:
            run_button = QPushButton("Plots")
        run_button.clicked.connect(lambda _, m=mode: self.run_action(m))
        button_layout.addWidget(run_button)
        self.run_buttons[mode] = run_button

        form_layout.addRow("", button_container)
        layout.addLayout(form_layout)

        # For the Plotter tab, create and add our PlotterWidget.
        if mode == Mode.PLOTTER:
            self.plotter_widget = PlotterWidget()
            layout.addWidget(self.plotter_widget)

        self.update_buttons()

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
            "")
        if folder_path:
            line_edit.setText(folder_path)

    def run_action(self, mode: Mode):
        custom_print(f"Run button clicked on page: {Constants.pages.get(mode, 'Unknown')}")

        if mode == Mode.PLOTTER:
            self.running_plotter = True
            folder_path = self.data_location_line_edit.text().strip()
            if os.path.isdir(folder_path):
                # Tell the PlotterWidget to update its plot.
                self.plotter_widget.update_plot(folder_path)
            else:
                custom_print("Invalid folder.")


        elif mode in [Mode.SCAN, Mode.MPPT]:
            self.running_left = True
            self.update_buttons()

            values = []
            for param, textbox in self.textboxes.get(mode, []):
                if param == "Trial Name":
                    self.trial_name = textbox.text()
                values.append(textbox.text())

            self.multi_controller = MultiController(
                trial_name=self.trial_name,
                date=self.today,
                plotting_mode=False)
            self.data_location_line_edit.setText(self.multi_controller.folder_path)
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
                # Wait loop; add any condition for finishing the run.
                threading.Event().wait(0.1)
        self.after_run(mode)

    def after_run(self, mode: Mode):
        self.running_left = False
        self.update_buttons()
        self.left_tabs.tabBar().setEnabled(True)
        while self.multi_controller.controllers:
            # Wait loop for multi controller to finish exiting gracefully.
            threading.Event().wait(0.1)

        self.multi_controller.controllers = None
        self.multi_controller = None

        custom_print(f"Run finished on page: {Constants.pages.get(mode, 'Unknown')}")

    def stop_action(self, mode: Mode):
        custom_print(f"Stop button clicked on page: {Constants.pages.get(mode, 'Unknown')}")

        # Signal all running threads to stop.
        self.stop_measurement_thread.set()

        # If your multi_controller spawns its own threads, signal them to stop as well.
        if self.multi_controller is not None:
            self.multi_controller.run(Mode.STOP)

        # Reset flags and update the UI.
        self.running_left = False
        self.update_buttons()
        self.left_tabs.tabBar().setEnabled(True)

        # Optionally, if your wait thread is still running, join it with a timeout.
        # if self.running_thread is not None and self.running_thread.is_alive():
        #     custom_print("Waiting for the worker thread to finish...")
        #     self.running_thread.join(timeout=2)  # Adjust timeout as needed.
        #     if self.running_thread.is_alive():
        #         custom_print("Warning: Worker thread did not finish in time.")
        #     else:
        #         custom_print("Worker thread stopped successfully.")

    def on_csv_changed(self, path):
        custom_print(f"CSV file or folder changed: {path}")
        if hasattr(self, 'plotter_widget'):
            # If a change is detected, update the plot.
            folder_path = self.data_location_line_edit.text().strip()
            self.plotter_widget.update_plot(folder_path)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
