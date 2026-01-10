import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QTabWidget,
    QMessageBox,
)
from PySide6.QtCore import Qt
from gui.results_viewer.plotter_widget import PlotterWidget
from gui.results_viewer.combine_plots import combine_plots_main
from gui.results_viewer.combine_plots import MINIMUM_MINUTES
from helper.global_helpers import get_logger
from constants import Constants

fileTypes = ("scan.csv", "mppt.csv", "compressedmppt.csv")
PLOTTINGKBTHRESHOLD = 10000

class PlotterPanel(QWidget):
    def __init__(self, default_folder: str = "", parent=None):
        super().__init__(parent)
        self.default_folder = default_folder
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- CSV Folder Search Bar ---
        self.data_location_line_edit = QLineEdit()
        self.data_location_line_edit.setText(self.default_folder)

        # Create a container for the line edit and buttons.
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(self.data_location_line_edit)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.open_folder_dialog)
        h_layout.addWidget(browse_button)

        # Create the "Create Plot(s)" button.
        create_plots_button = QPushButton("Create Plot(s)")
        create_plots_button.clicked.connect(self.create_plots)
        h_layout.addWidget(create_plots_button)

        # Create the "Combine Plots" button.
        combine_plots_button = QPushButton("Combine Plots")
        combine_plots_button.clicked.connect(self.combine_plots)
        h_layout.addWidget(combine_plots_button)

        form_layout.addRow("CSV Folder", container)

        layout.addLayout(form_layout)

        # --- Plot Container for QTabWidget of Plotters ---
        self.plot_container = QWidget()
        self.plot_container.setLayout(QVBoxLayout())
        layout.addWidget(self.plot_container)

    def open_folder_dialog(self):
        current_path = self.data_location_line_edit.text()

        start_path = current_path
        if not os.path.isdir(start_path):
            # Fallback to the default folder if the current text is not a valid directory
            start_path = self.default_folder

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Data Folder",
            start_path
        )

        if folder_path:
            self.data_location_line_edit.setText(folder_path)

    def create_plots(self):
        get_logger().log("Create Plot Button Pushed")
        folder_path = self.data_location_line_edit.text().strip()
        if os.path.isdir(folder_path):
            plot_groups = self.get_plot_groups(folder_path)
            self.update_plot_tabs(plot_groups)
        else:
            QMessageBox.information(self, "Error", "Invalid Plotting Folder.")

    def combine_plots(self):
        get_logger().log("Combine Plots Button Pushed")
        folder_path = self.data_location_line_edit.text().strip()
        if os.path.isdir(folder_path):
            plot_groups = combine_plots_main(folder_path)

            if plot_groups:
                get_logger().log(f"Successfully combined plots: {plot_groups}")
                self.create_plots()
            else:
                QMessageBox.information(self, "Error", f"No MPPT files found to combine. MPPT must be longer than {MINIMUM_MINUTES} minutes to combine")
        else:
            QMessageBox.information(self, "Error", "Invalid Plotting Folder.")

    def update_plot_tabs(self, plot_groups: dict):
        """Clear the plot container and create a QTabWidget with a tab for each plot group."""
        plot_layout = self.plot_container.layout()
        # Remove any existing widgets
        while plot_layout.count():
            child = plot_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        plot_tab_widget = QTabWidget()
        for title, filepaths in reversed(plot_groups.items()):
            plotter_widget = PlotterWidget()
            plotter_widget.update_plot(title, filepaths)
            plot_tab_widget.addTab(plotter_widget, title)
        plot_layout.addWidget(plot_tab_widget)

    def get_plot_groups(self, folder_path: str) -> dict:
        """
        Group CSV files into plot groups.
        This method mimics the grouping logic from your original getPlotGroups.
        """
        csv_files = sorted(
            [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(fileTypes)
            ]
        )
        # get_logger().log(csv_files)

        file_groups_dict = {}

        if not csv_files:
            QMessageBox.information(self,
                "Warning",
                "Selected file location has no plottable files")
            return file_groups_dict
        for file in csv_files:
            # get_logger().log(file)
            head, tail = os.path.split(file)
            # get_logger().log(head, tail)

            # use compressed file if above certain file size threshold
            if tail.endswith("__mppt.csv"):
                file_size_kb = os.path.getsize(file) / 1024
                if file_size_kb > PLOTTINGKBTHRESHOLD:
                    continue
            elif tail.endswith("__compressedmppt.csv"):
                try:
                    filename = file.replace("__compressedmppt", "__mppt")
                    file_size_kb = os.path.getsize(filename) / 1024
                    if file_size_kb < PLOTTINGKBTHRESHOLD:
                        continue
                except:
                    get_logger().log("no full mppt file found")

            params = tail.split("__")
            # Assume the last part before the extension indicates the file type
            filetype = params[-1].split(".")[0]
            # If "ID" is not present, use the second parameter as test_name
            test_name = params[1] if "ID" not in params[1] else ""
            name_parts = [val for val in [test_name, params[0], filetype] if val]
            plot_name = " ".join(name_parts)
            # get_logger().log(plot_name)
            file_groups_dict.setdefault(plot_name, []).append(file)
        get_logger().log(f"plotter groups: {file_groups_dict.keys()}")
        return file_groups_dict
