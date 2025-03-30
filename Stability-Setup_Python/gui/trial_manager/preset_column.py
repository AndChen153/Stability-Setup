from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QAbstractItemView
)
import os
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from constants import Mode, Constants
from helper.global_helpers import custom_print
import assets_rc


class PresetColumnWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Set up the overall vertical layout
        main_layout = QVBoxLayout(self)

        # Add a title at the top using a QLabel (non-editable)
        self.title_label = QLabel("Presets")
        main_layout.addWidget(self.title_label)

        # Create a QListWidget to hold the rows
        self.list_widget = QListWidget()
        # Enable dragging and dropping of items within this list
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        main_layout.addWidget(self.list_widget)

        # Add a couple of initial rows
        self.add_row("Preset 1")
        self.add_row("Preset 2")

        # Add the "Add Row" widget as the last item in the list widget
        self.add_button_item = QListWidgetItem(self.list_widget)
        self.add_row_widget = AddPresetRowWidget(self)
        self.add_button_item.setSizeHint(self.add_row_widget.sizeHint())
        self.list_widget.addItem(self.add_button_item)
        self.list_widget.setItemWidget(self.add_button_item, self.add_row_widget)

    def add_row(self, text, insert_index=None):
        """Insert a new row widget before the add button row."""
        new_item = QListWidgetItem()
        row_widget = PresetRow(text, self.list_widget)
        new_item.setSizeHint(row_widget.sizeHint())

        # If no explicit index is provided, insert before the last item (the add button)
        if insert_index is None:
            count = self.list_widget.count()
            insert_index = count - 1 if count > 0 else 0

        self.list_widget.insertItem(insert_index, new_item)
        self.list_widget.setItemWidget(new_item, row_widget)

    def add_new_row(self):
        """Callback for the add button to insert a new row."""
        self.add_row("New Item")


class PresetRow(QWidget):
    def __init__(self, text, parent_list):
        super().__init__()
        self.parent_list = parent_list

        # Set up a horizontal layout for the row
        layout = QHBoxLayout(self)

        # Row name is editable (QLineEdit)
        self.name_edit = QLineEdit(text)
        layout.addWidget(self.name_edit)

        start_icon_filepath = ":/icons/start.png"
        edit_icon_filepath = ":/icons/edit.png"
        delete_icon_filepath = ":/icons/delete.png"

        icon_size = QSize(20, 20) # Define a consistent size

        # --- Start Button ---
        self.start_button = QPushButton()
        start_icon = QIcon(start_icon_filepath)
        if not start_icon.isNull():
            self.start_button.setIcon(start_icon)
            self.start_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {start_icon_filepath}")
            self.start_button.setText("S") # Fallback
        self.start_button.setToolTip("Start Preset")

        # --- Edit Button ---
        self.edit_button = QPushButton()
        edit_icon = QIcon(edit_icon_filepath)
        if not edit_icon.isNull():
            self.edit_button.setIcon(edit_icon)
            self.edit_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {edit_icon_filepath}")
            self.edit_button.setText("E") # Fallback
        self.edit_button.setToolTip("View / Edit Preset")

        # --- Delete Button ---
        self.delete_button = QPushButton()
        delete_icon = QIcon(delete_icon_filepath)
        if not delete_icon.isNull():
            self.delete_button.setIcon(delete_icon)
            self.delete_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {delete_icon_filepath}")
            self.delete_button.setText("X") # Fallback
        self.delete_button.setToolTip("Delete Preset")
        self.delete_button.clicked.connect(self.remove_row)

        layout.addWidget(self.start_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

        layout.addStretch()

    def remove_row(self):
        """Removes this row from the list widget."""
        count = self.parent_list.count()
        for index in range(count):
            item = self.parent_list.item(index)
            widget = self.parent_list.itemWidget(item)
            if widget == self:
                self.parent_list.takeItem(index)
                break


class AddPresetRowWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        layout = QHBoxLayout(self)
        self.add_preset = QPushButton("Create New Preset")
        layout.addWidget(self.add_preset)
        layout.addStretch()
        self.add_preset.clicked.connect(self.handle_add)

    def handle_add(self):
        """When clicked, instruct the main widget to add a new row."""
        self.main_widget.add_new_row()

