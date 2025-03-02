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
    QCheckBox
)
from PySide6.QtCore import Qt
from gui.plotter_widget import PlotterWidget
from helper.global_helpers import custom_print

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

        self.checkbox = QCheckBox("Plot Full Data")
        self.checkbox.setChecked(False)  # Sets the checkbox as checked
        self.checkbox.toggled.connect(self.on_checkbox_toggled)
        h_layout.addWidget(self.checkbox)

        form_layout.addRow("CSV Folder", container)

        layout.addLayout(form_layout)

        # --- Plot Container for QTabWidget of Plotters ---
        self.plot_container = QWidget()
        self.plot_container.setLayout(QVBoxLayout())
        layout.addWidget(self.plot_container)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select CSV Folder", "")
        if folder_path:
            self.data_location_line_edit.setText(folder_path)

    def create_plots(self):
        folder_path = self.data_location_line_edit.text().strip()
        if os.path.isdir(folder_path):
            plot_groups = self.get_plot_groups(folder_path)
            self.update_plot_tabs(plot_groups)
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
        for title, filepaths in plot_groups.items():
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
                if f.lower().endswith(".csv")
            ]
        )
        file_groups_dict = {}
        for file in csv_files:
            head, tail = os.path.split(file)
            if self.checkbox.isChecked() and tail.endswith("__compressedmppt.csv"):
                continue
            elif not self.checkbox.isChecked() and tail.endswith("__mppt.csv"):
                continue
            params = tail.split("__")
            # Assume the last part before the extension indicates the file type
            filetype = params[-1].split(".")[0]
            # If "ID" is not present, use the second parameter as test_name
            test_name = params[1] if "ID" not in params[1] else ""
            name_parts = [val for val in [test_name, params[0], filetype] if val]
            plot_name = " ".join(name_parts)
            file_groups_dict.setdefault(plot_name, []).append(file)
        return file_groups_dict

    def on_checkbox_toggled(self, checked):
        if checked:
            QMessageBox.information(self,
                "Warning",
                "Plotting the complete dataset for MPPT trials could potentially cause the software to crash.")