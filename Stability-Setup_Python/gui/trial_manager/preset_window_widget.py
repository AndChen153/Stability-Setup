# preset_window_widget.py
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
import sys
from constants import Mode, Constants
from helper.global_helpers import custom_print
from gui.trial_manager.preset_column import PresetColumnWidget
from gui.trial_manager.preset_trial_column import TrialColumnWidget

# Container widget that holds the two list widgets side by side
class PresetQueueWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Two List Widgets Side by Side")
        layout = QHBoxLayout(self)

        # Left queue: presets
        self.left_queue = PresetColumnWidget()
        # Right queue: trials
        self.right_queue = TrialColumnWidget()

        min_column_width_presets = 400
        min_column_width_trials = 250
        self.left_queue.setMinimumWidth(min_column_width_presets)
        self.right_queue.setMinimumWidth(min_column_width_trials)

        layout.addWidget(self.left_queue)
        layout.addWidget(self.right_queue)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PresetQueueWidget()
    window.show()
    sys.exit(app.exec())
