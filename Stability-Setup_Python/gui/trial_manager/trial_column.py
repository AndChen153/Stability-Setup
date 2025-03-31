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
from PySide6.QtCore import QSize, Signal, Slot, Qt
import sys
from constants import Mode, Constants
from helper.global_helpers import custom_print
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.dragable_list import DraggableListWidget

class TrialColumnWidget(QWidget):
    delete_requested = Signal(Preset, Trial)
    new_trial = Signal(Preset, Trial)
    edit_requested = Signal(Preset, Trial)
    trial_moved = Signal(Trial, Preset, int)
    def __init__(self):
        super().__init__()
        self.selected_preset = None

        # Set up the overall vertical layout
        main_layout = QVBoxLayout(self)

        # Add a title at the top using a QLabel (non-editable)
        self.title_label = QLabel("Trials")
        main_layout.addWidget(self.title_label)

        # Create a QListWidget to hold the rows
        self.list_widget = DraggableListWidget(self)
        # Enable dragging and dropping of items within this list
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.trialMoved.connect(self.handle_item_moved)

        main_layout.addWidget(self.list_widget)

        # Add the "Add Row" widget as the last item in the list widget
        self.add_button_item = QListWidgetItem(self.list_widget)
        self.add_row_widget = AddTrialRowWidget(self)
        self.add_button_item.setSizeHint(self.add_row_widget.sizeHint())
        self.list_widget.addItem(self.add_button_item)
        self.list_widget.setItemWidget(self.add_button_item, self.add_row_widget)

    def add_row(self, trial: Trial, insert_index=None):
        """Insert a new row widget before the add button row."""
        # If no explicit index is provided, insert before the last item (the add button)
        if insert_index is None:
            count = self.list_widget.count()
            insert_index = count - 1 if count > 0 else 0

        new_item = QListWidgetItem()
        row_widget = TrialRow(insert_index, trial, self.list_widget)
        row_widget.delete_requested.connect(self._delete_requested)
        row_widget.edit_requested.connect(self._trial_edit)

        new_item.setSizeHint(row_widget.sizeHint())

        self.list_widget.insertItem(insert_index, new_item)
        self.list_widget.setItemWidget(new_item, row_widget)

    def add_new_row(self, mode):
        """Callback for the add button to insert a new row."""
        trial = Trial(mode, Constants.defaults[mode])
        self.add_row(trial)
        self._trial_created(trial)

    def clear_trials(self):
        """Removes all trial rows except the 'Add Trial' button row."""
        self.selected_preset = None
        # Iterate backwards when removing items to avoid index shifting issues
        for i in range(self.list_widget.count() - 1, -1, -1):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            # Check if the widget associated with the item is NOT AddTrialRowWidget
            if not isinstance(widget, AddTrialRowWidget):
                self.list_widget.takeItem(i) # Remove the item

    def on_trial_deletion_confirmed(self, trial: Trial):
        # Iterate through the list widget items to find the matching preset.
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget and widget.trial == trial:
                # Remove the item once deletion is confirmed.
                self.list_widget.takeItem(i)
                break

    @Slot(Trial, Preset, int)
    def handle_item_moved(self, trial, preset, new_index):
        custom_print(f"Trial moved: {trial} from preset {preset} moved to index {new_index}")
        self.trial_moved.emit(trial, preset, new_index)

    @Slot(Preset) # Decorate as a slot that accepts a Preset object
    def update_trials(self, selected_preset: Preset):
        """Clears existing trials and adds trials from the selected preset."""
        custom_print(f"Slot update_trials called for: {selected_preset.name if selected_preset else 'None'}")
        self.clear_trials() # Clear the list first
        self.selected_preset = selected_preset

        if selected_preset and selected_preset.trials:
            for idx, trial in enumerate(selected_preset.trials):
                self.add_row(trial, idx)
        else:
            # Handle cases where the preset is None or has no trials
            custom_print(f"No trials to display for '{selected_preset.name if selected_preset else 'N/A'}'.")

    @Slot(Trial)
    def _delete_requested(self, trial:Trial):
        custom_print(f"Delete requeseted for trial {trial}")
        self.delete_requested.emit(self.selected_preset, trial)

    @Slot(Trial)
    def _trial_created(self, trial:Trial):
        custom_print(f"{trial} Trial Created")
        self.new_trial.emit(self.selected_preset, trial)

    @Slot(Trial)
    def _trial_edit(self, trial:Trial):
        custom_print(f"{trial} Trial edited")
        self.edit_requested.emit(self.selected_preset, trial)

class TrialRow(QWidget):
    delete_requested = Signal(Trial)
    edit_requested = Signal(Trial)

    def __init__(self, insert_index:int, trial:Trial, parent_list):
        super().__init__()
        self.parent_list = parent_list

        self.trial = trial
        self.index = insert_index

        # Set up a horizontal layout for the row
        layout = QHBoxLayout(self)
        trial_name = Constants.run_modes[trial.trial_type]
        # Row name is non-editable (QLabel)
        self.name = QLabel(trial_name)
        layout.addWidget(self.name)

        # Add additional buttons for the row
        self.edit_button = QPushButton("View / Edit")
        layout.addWidget(self.edit_button)
        self.edit_button.clicked.connect(self._emit_edit_button_signal)

        self.delete_button = QPushButton("Delete")
        layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self._emit_remove_button_signal)
        layout.addStretch()

    @Slot()
    def _emit_remove_button_signal(self):
        self.delete_requested.emit(self.trial)

    @Slot()
    def _emit_edit_button_signal(self):
        self.edit_requested.emit(self.trial)

class AddTrialRowWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        layout = QHBoxLayout(self)
        self.add_scan = QPushButton("Add scan")
        self.add_mppt = QPushButton("Add mppt")
        layout.addWidget(self.add_scan)
        layout.addWidget(self.add_mppt)
        layout.addStretch()
        # Use lambda to ensure the handler is called on button click
        self.add_scan.clicked.connect(lambda: self.handle_add(Mode.SCAN))
        self.add_mppt.clicked.connect(lambda: self.handle_add(Mode.MPPT))

    def handle_add(self, mode):
        """When clicked, instruct the main widget to add a new row."""
        self.main_widget.add_new_row(mode)
