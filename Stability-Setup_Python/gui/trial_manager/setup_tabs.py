# gui/setup_tabs.py
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QMessageBox
from constants import Constants, Mode
from gui.trial_manager.setup_tab import SetupTab
from gui.trial_manager.preset_manager import PresetManager

class SetupTabs(QWidget):
    def __init__(self, user_settings_json, tab_components, textboxes, common_param_lineedits, parent=None):
        """
        :param preset_manager: A reference to the preset manager.
        :param common_param_lineedits: A dictionary of common parameter QLineEdits.
        """
        super().__init__(parent)

        self.tab_components = tab_components  # Store each SetupTab by mode.
        self.tab_widget = QTabWidget(self)
        self.textboxes = textboxes

        self.preset_dropdown = {}  # This is now managed inside each SetupTab
        self.preset_manager = PresetManager(
            user_settings_json, self.textboxes, self.preset_dropdown, self.show_popup
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

        # Loop through all run modes (e.g., SCAN and MPPT) and create a SetupTab for each.
        for mode, page_title in Constants.run_modes.items():
            tab_component = SetupTab(mode, self.preset_manager, common_param_lineedits)
            self.preset_dropdown[mode] = tab_component.preset_dropdown
            self.textboxes[mode] = tab_component.textboxes
            self.tab_components[mode] = tab_component
            self.tab_widget.addTab(tab_component, page_title)

        self.preset_manager.populate_all()

    def connect_signals(self, run_callback, stop_callback):
        """Connect each SetupTab's run and stop signals to the given callbacks."""
        for tab in self.tab_components.values():
            tab.runRequested.connect(run_callback)
            tab.stopRequested.connect(stop_callback)

    def get_tab_widget(self):
        """Return the internal QTabWidget if needed."""
        return self.tab_widget

    def set_tab_bar(self, set_value):
        self.tab_widget.tabBar().setEnabled(set_value)

    def show_popup(self, message: str):
        QMessageBox.information(self, "Notification", message)