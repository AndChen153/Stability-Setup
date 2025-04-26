import sys
import json
import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QScrollArea,
    QPushButton
)
from PySide6.QtCore import Qt, Signal
from constants import Mode, Constants
from helper.global_helpers import custom_print

class NoScrollSpinBox(QSpinBox):
    def wheelEvent(self, event):
        # Ignore the wheel event so the value doesn't change when scrolling.
        event.ignore()

class IDWidget(QWidget):
    refreshRequested = Signal()

    def __init__(self, json_file, parent=None):
        super().__init__(parent)
        # set in other class
        self.connected_Arduino = []
        self.json_file = json_file
        self.data = {}  # This will hold only the "arduino_ids" section.
        self.spinboxes = {}  # To store spinboxes by key.
        self.load_json()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with a scrollable layout and a refresh button."""
        outer_layout = QVBoxLayout(self)

        # Create a QScrollArea to make the content scrollable.
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create a container widget that will hold our actual UI content.
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_widget.setLayout(self.container_layout)

        # Set the container widget as the scroll area's widget.
        scroll_area.setWidget(self.container_widget)

        # Add the scroll area to the outer layout.
        outer_layout.addWidget(scroll_area)

        # Create a refresh button and connect its clicked signal to a local slot.
        refresh_button = QPushButton("Refresh Connected")
        refresh_button.clicked.connect(self.on_refresh_clicked)
        outer_layout.addWidget(refresh_button)

        self.refresh_ui()

    def on_value_changed(self, key, new_value):
        """Handle updates when the spinbox value changes."""
        self.data[key] = new_value
        spinbox = self.spinboxes.get(key)
        if spinbox:
            if new_value == -1:
                spinbox.setStyleSheet("background-color: red;")
            else:
                spinbox.setStyleSheet("")
        custom_print(f"Updated {key} to {new_value}")
        self.save_json()

    def load_json(self):
        """Load JSON data from the specified file and extract the 'arduino_ids' section."""
        try:
            with open(self.json_file, "r") as f:
                full_data = json.load(f)
            self.data = full_data.get("arduino_ids", {})
        except Exception as e:
            custom_print(f"Error loading JSON: {e}")
            self.data = {}

    def save_json(self):
        """
        Save the updated arduino_ids back to the centralized JSON file.
        This function loads the full file first, updates only the 'arduino_ids' section,
        and then writes it back.
        """
        try:
            # Load the full data from the file if it exists.
            if os.path.exists(self.json_file):
                with open(self.json_file, "r") as f:
                    full_data = json.load(f)
            else:
                full_data = {}
            # Update the 'arduino_ids' section with current data.
            full_data["arduino_ids"] = self.data
            with open(self.json_file, "w") as f:
                json.dump(full_data, f, indent=4)
            custom_print("JSON saved.")
            self.refresh_ui()
        except Exception as e:
            custom_print(f"Error saving JSON: {e}")

    def clear_layout(self, layout):
        """Recursively clear all items from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def refresh_ui(self):
        """
        Refresh the UI and separate entries into two sections:
        one for connected IDs and one for disconnected IDs.
        Additionally, highlight in red any spinboxes whose value is unknown
        or if the same value appears more than once.
        """
        # Use the container_layout (which is inside the scroll area).
        main_layout = self.container_layout
        if main_layout is None:
            return

        # Clear the existing layout.
        self.clear_layout(main_layout)
        self.spinboxes = {}

        # Count occurrences of each value to detect duplicates.
        value_counts = {}
        for key, value in self.data.items():
            value_counts[value] = value_counts.get(value, 0) + 1

        # Create separate layouts for connected and disconnected sections.
        connected_layout = QVBoxLayout()
        disconnected_layout = QVBoxLayout()

        # Add header labels for clarity.
        connected_header = QLabel("Connected Arduinos ⓘ")
        connected_header.setToolTip("Every Arduino must be assigned a unique ID number")
        connected_header.setStyleSheet("font-weight: bold;")
        connected_layout.addWidget(connected_header)

        disconnected_header = QLabel("Disconnected Arduinos ⓘ")
        disconnected_header.setToolTip("Every Arduino must be assigned a unique ID number")
        disconnected_header.setStyleSheet("font-weight: bold;")
        disconnected_layout.addWidget(disconnected_header)

        # Iterate over each key-value pair in the 'arduino_ids' data.
        for key, value in self.data.items():
            row_layout = QHBoxLayout()
            key_label = QLabel(key)
            key_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            row_layout.addWidget(key_label)

            spinbox = NoScrollSpinBox()
            spinbox.setRange(-1, 1000000)
            spinbox.setValue(value)
            spinbox.valueChanged.connect(lambda new_val, k=key: self.on_value_changed(k, new_val))
            row_layout.addWidget(spinbox)

            self.spinboxes[key] = spinbox

            # Highlight in red if the value is unknown or if duplicated.
            if value == Constants.unknown_Arduino_ID or value_counts.get(value, 0) > 1:
                spinbox.setStyleSheet("background-color: red;")
            else:
                spinbox.setStyleSheet("")

            # Place the row in the correct section.
            if key in self.connected_Arduino:
                connected_layout.addLayout(row_layout)
            else:
                disconnected_layout.addLayout(row_layout)

        # Add the two sections to the main layout with spacing.
        main_layout.addLayout(connected_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(disconnected_layout)
        main_layout.addStretch()
        self.update()

    def on_refresh_clicked(self):
        """
        Slot called when the refresh button is clicked.
        It emits the refreshRequested signal.
        """
        custom_print("Refresh button clicked in IDWidget.")
        self.refreshRequested.emit()
