# preset_window_widget.py
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QAbstractItemView,
    QSizePolicy,
    QFrame,
)
import sys
from constants import Mode, Constants
from helper.global_helpers import logger
from gui.trial_manager.preset_column import PresetColumnWidget
from gui.trial_manager.trial_column import TrialColumnWidget
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.preset_loader import PresetManager
from gui.trial_manager.setup_tab import SetupTab
from PySide6.QtCore import Slot, Signal

# Container widget that holds the two list widgets side by side
class PresetQueueWidget(QWidget):
    run_start = Signal(Preset)
    def __init__(self, presetsJson):
        super().__init__()
        self.setWindowTitle("Two List Widgets Side by Side")
        self.currently_selected_preset:Preset = None
        self.currently_selected_trial:Trial = None

        self.preset_manager = PresetManager(presetsJson)
        self.presets = self.preset_manager.load_presets_from_json()

        # Right queue: trials
        self.trials_column = TrialColumnWidget()
        min_column_width_trials = 250
        self.trials_column.setMinimumWidth(min_column_width_trials)
        self.trials_column.delete_requested.connect(self.handle_trial_deleted)
        self.trials_column.new_trial.connect(self.handle_trial_created)
        self.trials_column.edit_requested.connect(self.handle_trial_edit_button)
        self.trials_column.trial_moved.connect(self.handle_trial_moved)

        # Left column
        self.preset_column = PresetColumnWidget(self.presets)
        self.preset_column.preset_selected.connect(self.trials_column.update_trials)
        self.preset_column.preset_added.connect(self.handle_preset_added)
        self.preset_column.preset_renamed.connect(self.handle_preset_renamed)
        self.preset_column.preset_deleted.connect(self.handle_preset_deleted)
        self.preset_column.preset_moved.connect(self.handle_preset_moved)
        self.preset_column.preset_start.connect(self.handle_preset_start)

        # Set left column width
        min_column_width_presets = 270
        self.preset_column.setMinimumWidth(min_column_width_presets)

        self.param_tab = SetupTab(None, {})

        self.layout = QHBoxLayout(self)
        self.preset_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.trials_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.param_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add widgets with equal stretch factors
        self.layout.addWidget(self.preset_column, 1)
        line1 = QFrame()
        line1.setFrameShape(QFrame.VLine)
        line1.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line1)

        self.layout.addWidget(self.trials_column, 1)
        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)
        line2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line2)
        self.layout.addWidget(self.param_tab, 1)

    def clear_params_tab(self, reset = True):
        if self.param_tab:
            if self.layout and self.layout.indexOf(self.param_tab) != -1:
                self.layout.removeWidget(self.param_tab)
            self.param_tab.deleteLater()
            if reset:
                self.param_tab = SetupTab(None, {})
                self.layout.addWidget(self.param_tab, 1)
            else:
                self.param_tab = None

    @Slot(Preset)
    def handle_preset_selection(self, selected_preset: Preset | None):
        """Slot to handle when a preset is selected in the left list."""
        self.currently_selected_preset = selected_preset
        self.trials_column.update_trials(
            selected_preset
        )  # Update the trial list display
        self.clear_params_tab()

    @Slot(Preset)
    def handle_preset_added(self, new_preset: Preset):
        """Slot to add the new Preset object to our main list."""
        logger.log(
            f"PresetQueueWidget: Adding preset '{new_preset.name}' to internal list."
        )

        self.presets.append(new_preset)
        logger.log(
            f"PresetQueueWidget: Preset list updated. Count: {len(self.presets)}"
        )
        self.currently_selected_preset = new_preset
        self.trials_column.update_trials(new_preset)
        self.preset_manager.save_presets_to_json(self.presets)
        self.clear_params_tab()

    @Slot(Preset)
    def handle_preset_deleted(self, preset_to_delete: Preset):
        """Slot to remove the Preset object from our main list."""
        logger.log(
            f"PresetQueueWidget: Deleting preset '{preset_to_delete.name}' from internal list."
        )

        # Optional: Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the preset '{preset_to_delete.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        #
        if reply == QMessageBox.StandardButton.No:
            logger.log("PresetQueueWidget: Deletion cancelled by user.")
            return

        self.clear_params_tab()

        try:
            # Check if the deleted preset was the selected one
            was_selected = self.currently_selected_preset == preset_to_delete

            self.presets.remove(
                preset_to_delete
            )  # Preset has __eq__

            self.preset_column.on_preset_deletion_confirmed(preset_to_delete)
            logger.log(
                f"PresetQueueWidget: Preset list updated. Count: {len(self.presets)}"
            )

            # If the deleted item was selected, clear the trial view
            if was_selected:
                self.currently_selected_preset = None
            self.trials_column.update_trials(None)  # Clear right panel

            # Optionally trigger save or indicate unsaved changes
            self.preset_manager.save_presets_to_json(self.presets)

        except ValueError:
            logger.log(
                f"PresetQueueWidget: Error! Preset '{preset_to_delete.name}' not found in internal list for deletion."
            )

    @Slot(Preset, str)
    def handle_preset_renamed(self, preset: Preset, new_name: str):
        """Slot to update the name of the Preset object in our main list."""

        if preset in self.presets:
            old_name = preset.name
            preset.name = new_name  # Update the actual Preset object's name
            logger.log(f"Renamed preset '{old_name}' to '{preset.name}'.")

            # If the renamed preset is the currently selected one,
            # we might want to update related UI elements (e.g., TrialColumn title if it shows preset name)
            if self.currently_selected_preset == preset:
                # self.right_queue.title_label.setText(f"Trials for '{new_name}'") # Example update
                pass  # update_trials might implicitly handle this if it redraws based on the object

            self.preset_manager.save_presets_to_json(self.presets)
        else:
            logger.log(
                f"PresetQueueWidget: Error! Preset object not found in internal list for rename."
            )

    @Slot(Preset, int)
    def handle_preset_moved(self, preset:Preset, new_index: int):
        if not preset:
            return

        current_index = self.presets.index(preset)

        # Remove the trial from its current position
        self.presets.pop(current_index)

        # Insert it at the new position, making sure the index is within bounds
        if new_index >= len(self.presets):
            self.presets.append(preset)
        else:
            self.presets.insert(new_index, preset)
        self.preset_manager.save_presets_to_json(self.presets)

    @Slot(Preset)
    def handle_preset_start(self, preset:Preset):
        logger.log(f"Start requested for '{preset.name}'")
        self.handle_preset_selection(preset)
        self.run_start.emit(preset)


    @Slot(Preset, Trial)
    def handle_trial_deleted(self, preset: Preset, trial: Trial):
        """Slot to remove the Preset object from our main list."""
        logger.log(
            f"PresetQueueWidget: Deleting trial '{Constants.run_modes[trial.trial_type]}' from internal list."
        )

        # Optional: Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the {Constants.run_modes[trial.trial_type]} trial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        #
        if reply == QMessageBox.StandardButton.No:
            logger.log("PresetQueueWidget: Deletion cancelled by user.")
            return

        self.clear_params_tab()

        try:
            was_selected = self.currently_selected_trial == trial
            print(preset)
            preset.trials.remove(
                trial
            )  # Assumes Preset has __eq__ or object identity works

            self.trials_column.on_trial_deletion_confirmed(trial)
            logger.log(
                f"PresetQueueWidget: Trial list updated. Count: {len(preset.trials)}"
            )

            # If the deleted item was selected, clear the trial view
            if was_selected:
                self.currently_selected_trial = None

            self.trials_column.update_trials(
                preset
            )

            # Optionally trigger save or indicate unsaved changes
            self.preset_manager.save_presets_to_json(self.presets)

        except ValueError:
            logger.log(
                f"PresetQueueWidget: Error! {Constants.run_modes[trial.trial_type]} Trial not found in internal list for deletion."
            )

    @Slot(Preset, Trial)
    def handle_trial_created(self, preset: Preset, trial: Trial):
        logger.log(
            f"PresetQueueWidget: Creating '{trial}'"
        )

        preset.trials.append(trial)
        self.handle_trial_edit_button(preset, trial)
        logger.log(
            f"PresetQueueWidget: Preset trial list updated. Count: {len(preset.trials)}"
        )
        self.preset_manager.save_presets_to_json(self.presets)

    @Slot(Preset, Trial)
    def handle_trial_edit_button(self, preset:Preset, trial:Trial):
        logger.log(
            f"PresetQueueWidget: Editing '{trial}'"
        )

        self.clear_params_tab(reset=False)

        # Create a new SetupTab with the updated mode and parameters
        self.param_tab = SetupTab(mode=trial.trial_type, params=trial.params)
        self.param_tab.valueChanged.connect(self.handle_trial_value_edit)

        self.currently_selected_trial = trial
        self.param_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the new widget to the layout
        self.layout.addWidget(self.param_tab, 1)

    @Slot(list)
    def handle_trial_value_edit(self, params: dict[str, str]):
        logger.log(
            f"PresetQueueWidget: Set new params: {params}"
        )

        self.currently_selected_trial.params = params

        self.preset_manager.save_presets_to_json(self.presets)

    @Slot(Trial, Preset, int)
    def handle_trial_moved(self, trial:Trial, preset:Preset, new_index:int):
        if not preset or trial not in preset.trials:
            return
        current_index = preset.trials.index(trial)

        # Remove the trial from its current position
        preset.trials.pop(current_index)

        # Insert it at the new position, making sure the index is within bounds
        if new_index >= len(preset.trials):
            preset.trials.append(trial)
        else:
            preset.trials.insert(new_index, trial)
        self.preset_manager.save_presets_to_json(self.presets)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = PresetQueueWidget()
    window.show()
    sys.exit(app.exec())
