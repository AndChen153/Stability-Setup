# gui/setup_tabs.py
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QMessageBox
from constants import Constants, Mode
from gui.trial_manager.setup_tab import SetupTab
from gui.trial_manager.preset_loader import PresetManager

class SetupTabs(QWidget):
    def __init__(self, tab_components, textboxes, parent=None):
        super().__init__(parent)

        self.tab_components = tab_components  # Store each SetupTab by mode.
        self.tab_widget = QTabWidget(self)
        self.textboxes = textboxes

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

        # Loop through all run modes (e.g., SCAN and MPPT) and create a SetupTab for each.
        for mode, page_title in Constants.run_modes.items():
            tab_component = SetupTab(mode, [])
            self.textboxes[mode] = tab_component.textboxes
            self.tab_components[mode] = tab_component
            self.tab_widget.addTab(tab_component, page_title)


    def connect_signals(self, run_callback, stop_callback):
        """Connect each SetupTab's run and stop signals to the given callbacks."""
        pass

    def get_tab_widget(self):
        """Return the internal QTabWidget if needed."""
        return self.tab_widget

    def set_tab_bar(self, set_value):
        self.tab_widget.tabBar().setEnabled(set_value)

    def show_popup(self, message: str):
        QMessageBox.information(self, "Notification", message)