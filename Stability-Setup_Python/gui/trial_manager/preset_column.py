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
    QAbstractItemView,
)
import os
import assets_rc
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal, Slot, Qt
from constants import Mode, Constants
from helper.global_helpers import get_logger
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.dragable_list import DraggableListWidget

class PresetColumnWidget(QWidget):
    preset_selected = Signal(Preset)
    preset_added = Signal(Preset)
    # Emitted BEFORE a preset is removed from the list/data model
    preset_deleted = Signal(Preset)
     # Emitted AFTER a preset's name has been validated and is ready to be changed
    preset_renamed = Signal(Preset, str)
    preset_moved = Signal(Preset, int)
    preset_start = Signal(Preset)

    def __init__(self, presets):
        super().__init__()
        self.presets = presets

        # Set up the overall vertical layout
        main_layout = QVBoxLayout(self)

        # Add a title at the top using a QLabel (non-editable)
        self.title_label = QLabel("Presets")
        main_layout.addWidget(self.title_label)

        # Create a QListWidget to hold the rows
        self.list_widget = DraggableListWidget(self)
        # Enable dragging and dropping of items within this list
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.presetMoved.connect(self.handle_item_moved)

        # Connect itemClicked for selection -> show correct trial list
        self.list_widget.itemClicked.connect(self.handle_row_clicked_or_selected)
        # Also connect currentItemChanged for selection via keyboard/programmatically
        main_layout.addWidget(self.list_widget)

        # Populate Rows
        for name in self.presets:
            self.add_row(name)

        # Add the "Add Row" widget as the last item in the list widget
        self.add_button_item = QListWidgetItem(self.list_widget)

        self.add_new_preset_button = QPushButton("Create New Preset")
        self.add_new_preset_button.clicked.connect(self._handle_add_request)

        self.list_widget.addItem(self.add_button_item)
        self.list_widget.setItemWidget(self.add_button_item, self.add_new_preset_button)

    def add_row(self, preset:Preset, insert_index=None, select=False):
        """Insert a new row widget before the add button row."""
        new_item = QListWidgetItem()
        row_widget = PresetRow(preset, self.list_widget, new_item)
        row_widget.edit_button_clicked.connect(self.handle_row_clicked_or_selected)
        row_widget.name_changed.connect(self._handle_preset_name_edit)
        row_widget.delete_requested.connect(self._handle_preset_removal)
        row_widget.start_button_clicked.connect(self._handle_preset_start)

        new_item.setSizeHint(row_widget.sizeHint())

        # If no explicit index is provided, insert before the last item (the add button)
        if insert_index is None:
            count = self.list_widget.count()
            insert_index = count - 1 if count > 0 else 0

        self.list_widget.insertItem(insert_index, new_item)
        self.list_widget.setItemWidget(new_item, row_widget)
        if select:
            self.list_widget.setCurrentItem(new_item)


    def handle_row_clicked_or_selected(self, item: QListWidgetItem):
        widget = self.list_widget.itemWidget(item)

        if isinstance(widget, PresetRow):
            preset = widget.preset # Get current name from QLineEdit
            get_logger().log(f"Preset row clicked/selected: '{preset.name}' at index {self.list_widget.row(item)}")

            self.preset_selected.emit(preset)
            self.list_widget.setCurrentItem(item) # Ensure visual selection

    def on_preset_deletion_confirmed(self, preset: Preset):
        # Iterate through the list widget items to find the matching preset.
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget and widget.preset == preset:
                # Remove the item
                self.list_widget.takeItem(i)
                break

    @Slot(Preset, int)
    def handle_item_moved(self, preset, new_index):
        get_logger().log(f"Preset moved: preset {preset} moved to index {new_index}")
        self.preset_moved.emit(preset, new_index)

    @Slot()
    def _handle_add_request(self):
        get_logger().log("Sending new preset signal")
        new_preset = Preset(name="New Preset") # Create with default vals
        # Emit the signal to notify the parent *before* adding visually
        self.preset_added.emit(new_preset)
        # Add preset to page
        self.add_row(new_preset, select = True)

    @Slot()
    def _handle_preset_name_edit(self, preset:Preset, name:str):
        self.preset_renamed.emit(preset, name)

    @Slot()
    def _handle_preset_removal(self, preset:Preset):
        self.preset_deleted.emit(preset)

    @Slot(Preset)
    def _handle_preset_start(self, preset:Preset):
        get_logger().log(f"PresetRow: Start requested for '{preset.name}'")
        self.preset_start.emit(preset)

class PresetRow(QWidget):
    delete_requested = Signal(Preset)
    name_changed = Signal(Preset, str)
    edit_button_clicked = Signal(QListWidgetItem)
    start_button_clicked = Signal(Preset)


    def __init__(self, preset:Preset, parent_list: QListWidget, list_item: QListWidgetItem):
        super().__init__()
        self.parent_list = parent_list
        self.list_item = list_item  # Store the item this widget belongs to
        self.preset = preset

        # Set up a horizontal layout for the row
        layout = QHBoxLayout(self)

        # Row name is editable (QLineEdit)
        name = preset.name
        self.name_edit = QLineEdit(name)
        self.name_edit.editingFinished.connect(self._handle_name_editing_finished)

        layout.addWidget(self.name_edit)

        start_icon_filepath = ":/icons/start.png"
        edit_icon_filepath = ":/icons/edit.png"
        delete_icon_filepath = ":/icons/delete.png"

        icon_size = QSize(20, 20)  # Define a consistent size

        # --- Start Button ---
        self.start_button = QPushButton()
        start_icon = QIcon(start_icon_filepath)
        if not start_icon.isNull():
            self.start_button.setIcon(start_icon)
            self.start_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {start_icon_filepath}")
            self.start_button.setText("S")  # Fallback
        self.start_button.setToolTip("Start Preset")
        self.start_button.clicked.connect(self._request_start)

        # --- Edit Button ---
        self.edit_button = QPushButton()
        edit_icon = QIcon(edit_icon_filepath)
        if not edit_icon.isNull():
            self.edit_button.setIcon(edit_icon)
            self.edit_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {edit_icon_filepath}")
            self.edit_button.setText("E")  # Fallback
        self.edit_button.setToolTip("View / Edit Preset")
        self.edit_button.clicked.connect(self._emit_edit_button_signal)

        # --- Delete Button ---
        self.delete_button = QPushButton()
        delete_icon = QIcon(delete_icon_filepath)
        if not delete_icon.isNull():
            self.delete_button.setIcon(delete_icon)
            self.delete_button.setIconSize(icon_size)
        else:
            print(f"Warning: Could not load icon: {delete_icon_filepath}")
            self.delete_button.setText("X")  # Fallback
        self.delete_button.setToolTip("Delete Preset")
        self.delete_button.clicked.connect(self._request_delete)
        # self.delete_button.clicked.connect(self.remove_row)

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

    @Slot()
    def _emit_edit_button_signal(self):
        self.edit_button_clicked.emit(self.list_item)

    @Slot()
    def _handle_name_editing_finished(self):
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.preset.name:
            get_logger().log(f"PresetRow: Name edit finished for '{self.preset.name}'. New potential name: '{new_name}'")
            # Emit signal with the Preset object and the new desired name
            self.name_changed.emit(self.preset, new_name)
        else:
             # If name is unchanged or empty, reset QLineEdit to original name
             self.name_edit.setText(self.preset.name)

    @Slot()
    def _emit_edit_button_signal(self):
        self.edit_button_clicked.emit(self.list_item)

    @Slot()
    def _request_delete(self):
        get_logger().log(f"PresetRow: Delete requested for '{self.preset.name}'")
        self.delete_requested.emit(self.preset)

    @Slot()
    def _request_start(self):
        get_logger().log(f"PresetRow: Start requested for '{self.preset.name}'")
        self.start_button_clicked.emit(self.preset)


