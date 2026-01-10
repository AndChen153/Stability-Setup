from PySide6.QtWidgets import (
    QListWidget,
)
from helper.global_helpers import get_logger
from PySide6.QtCore import Signal, Slot

# --- New subclass to capture drag/drop moves ---
class DraggableListWidget(QListWidget):
    # This signal will emit: trial, preset, what, new_index
    trialMoved = Signal(object, object, int)
    presetMoved = Signal(object, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragged_item = None

    def startDrag(self, supportedActions):
        # Record the item that is being dragged.
        self.dragged_item = self.currentItem()
        super().startDrag(supportedActions)

    def dropEvent(self, event):
        super().dropEvent(event)
        if self.dragged_item is not None:
            # Determine the new index of the dragged item.
            new_index = self.row(self.dragged_item)
            widget = self.itemWidget(self.dragged_item)
            # Only emit if the widget is a TrialRow (i.e. has a 'trial' attribute)
            if widget and hasattr(widget, 'trial'):
                trial = widget.trial
                # Assuming the list widget's parent is the TrialColumnWidget.
                preset = self.parent().selected_preset if self.parent() and hasattr(self.parent(), 'selected_preset') else None
                self.trialMoved.emit(trial, preset, new_index)
            elif widget and hasattr(widget, 'preset'):
                preset = widget.preset
                # Assuming the list widget's parent is the TrialColumnWidget.
                self.presetMoved.emit(preset, new_index)
            self.dragged_item = None
