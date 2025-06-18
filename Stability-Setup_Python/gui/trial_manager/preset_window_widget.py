# preset_window_widget.py
"""
Preset Queue Widget with improved architecture using ConfigManager.

Refactored to use the centralized configuration management system
instead of direct JSON handling.
"""
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QFrame,
)
import sys
from pathlib import Path
from typing import Optional, List
from constants import Constants
from helper.global_helpers import get_logger
from gui.trial_manager.preset_column import PresetColumnWidget
from gui.trial_manager.trial_column import TrialColumnWidget
from gui.trial_manager.preset_data_class import Preset, Trial
from gui.trial_manager.setup_tab import SetupTab
from core.config_manager import ConfigManager
from core.error_handler import get_error_handler, with_error_handling
from PySide6.QtCore import Slot, Signal

class PresetQueueWidget(QWidget):
    """
    Widget for managing measurement presets and trials.

    Refactored to use ConfigManager for centralized configuration management
    instead of direct JSON handling through PresetManager.
    """
    run_start = Signal(Preset)

    def __init__(self, config_file_path: str):
        super().__init__()
        self.setWindowTitle("Preset Queue Manager")

        # Initialize core components
        self.config_manager = ConfigManager(Path(config_file_path))
        self.error_handler = get_error_handler()

        # Current selections
        self.currently_selected_preset: Optional[Preset] = None
        self.currently_selected_trial: Optional[Trial] = None

        # Load presets from configuration
        self.presets = self._load_presets_from_config()

        # Initialize UI components
        self._init_ui_components()
        self._setup_layout()
        self._connect_signals()

    def _init_ui_components(self) -> None:
        """Initialize UI components."""
        # Right column: trials
        self.trials_column = TrialColumnWidget()
        self.trials_column.setMinimumWidth(250)

        # Left column: presets
        self.preset_column = PresetColumnWidget(self.presets)
        self.preset_column.setMinimumWidth(270)

        # Parameters tab
        self.param_tab = SetupTab(None, {})

    def _setup_layout(self) -> None:
        """Set up the widget layout."""
        self.layout = QHBoxLayout(self)

        # Set size policies
        self.preset_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.trials_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.param_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add widgets with separators
        self.layout.addWidget(self.preset_column, 1)

        # Vertical separator
        line1 = QFrame()
        line1.setFrameShape(QFrame.VLine)
        line1.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line1)

        self.layout.addWidget(self.trials_column, 1)

        # Vertical separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)
        line2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line2)

        self.layout.addWidget(self.param_tab, 1)

    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Trial column signals
        self.trials_column.delete_requested.connect(self.handle_trial_deleted)
        self.trials_column.new_trial.connect(self.handle_trial_created)
        self.trials_column.edit_requested.connect(self.handle_trial_edit_button)
        self.trials_column.trial_moved.connect(self.handle_trial_moved)

        # Preset column signals
        self.preset_column.preset_selected.connect(self.trials_column.update_trials)
        self.preset_column.preset_added.connect(self.handle_preset_added)
        self.preset_column.preset_renamed.connect(self.handle_preset_renamed)
        self.preset_column.preset_deleted.connect(self.handle_preset_deleted)
        self.preset_column.preset_moved.connect(self.handle_preset_moved)
        self.preset_column.preset_start.connect(self.handle_preset_start)

    @with_error_handling(get_error_handler(), "Loading presets", return_value=[])
    def _load_presets_from_config(self) -> List[Preset]:
        """
        Load presets from configuration file.

        Returns:
            List of Preset objects loaded from configuration
        """
        try:
            # Load existing presets from config file
            if not self.config_manager.config_file.exists():
                get_logger().log("Config file not found, starting with empty presets")
                return []

            with open(self.config_manager.config_file, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)

            presets_data = data.get("presets", {})
            loaded_presets = []

            for preset_id, preset_info in presets_data.items():
                trial_name = preset_info.get("trial_name", "Unnamed Preset")
                trials_data = preset_info.get("trial", [])

                trials = []
                for trial_data in trials_data:
                    trial_type_str = trial_data.get("trial_type", "")
                    trial_id = trial_data.get("trial_id", "")
                    trial_params = trial_data.get("trial_params", {})

                    # Convert trial type string to Mode enum
                    trial_type = Constants.run_modes_reversed.get(trial_type_str)
                    if trial_type:
                        trials.append(Trial(trial_type, trial_params, trial_id))
                    else:
                        get_logger().log(f"Unknown trial type: {trial_type_str}")

                loaded_presets.append(Preset(trial_name, preset_id, trials))

            get_logger().log(f"Loaded {len(loaded_presets)} presets from configuration")
            return loaded_presets

        except Exception as e:
            self.error_handler.handle_exception(e, "Failed to load presets from configuration")
            return []

    @with_error_handling(get_error_handler(), "Saving presets")
    def _save_presets_to_config(self) -> None:
        """Save current presets to configuration file."""
        try:
            # Load existing configuration to preserve other settings
            config_data = {}
            if self.config_manager.config_file.exists():
                with open(self.config_manager.config_file, 'r', encoding='utf-8') as f:
                    import json
                    config_data = json.load(f)

            # Convert presets to dictionary format
            presets_data = {}
            for preset in self.presets:
                preset_dict = {
                    "trial_name": preset.name,
                    "trial": []
                }

                for trial in preset.trials:
                    trial_dict = {
                        "trial_type": Constants.run_modes[trial.trial_type],
                        "trial_id": str(trial.id),
                        "trial_params": trial.params
                    }
                    preset_dict["trial"].append(trial_dict)

                presets_data[str(preset.id)] = preset_dict

            # Update configuration data
            config_data["presets"] = presets_data

            # Save to file
            with open(self.config_manager.config_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(config_data, f, indent=4)

            get_logger().log(f"Saved {len(self.presets)} presets to configuration")

        except Exception as e:
            self.error_handler.handle_exception(e, "Failed to save presets to configuration")

    def clear_params_tab(self, reset: bool = True) -> None:
        """Clear the parameters tab and optionally reset it."""
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
    def handle_preset_selection(self, selected_preset: Optional[Preset]) -> None:
        """Handle when a preset is selected in the left list."""
        self.currently_selected_preset = selected_preset
        self.trials_column.update_trials(selected_preset)
        self.clear_params_tab()

    @Slot(Preset)
    def handle_preset_added(self, new_preset: Preset) -> None:
        """Handle adding a new preset to the list."""
        get_logger().log(f"Adding preset '{new_preset.name}' to internal list")

        self.presets.append(new_preset)
        self.currently_selected_preset = new_preset
        self.trials_column.update_trials(new_preset)
        self._save_presets_to_config()
        self.clear_params_tab()

        get_logger().log(f"Preset list updated. Count: {len(self.presets)}")

    @Slot(Preset)
    def handle_preset_deleted(self, preset_to_delete: Preset) -> None:
        """Handle deleting a preset from the list."""
        get_logger().log(f"Deleting preset '{preset_to_delete.name}' from internal list")

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the preset '{preset_to_delete.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            get_logger().log("Deletion cancelled by user")
            return

        self.clear_params_tab()

        try:
            # Check if the deleted preset was the selected one
            was_selected = self.currently_selected_preset == preset_to_delete

            self.presets.remove(preset_to_delete)
            self.preset_column.on_preset_deletion_confirmed(preset_to_delete)

            # If the deleted item was selected, clear the trial view
            if was_selected:
                self.currently_selected_preset = None
                self.trials_column.update_trials(None)

            # Save changes to configuration
            self._save_presets_to_config()

            get_logger().log(f"Preset list updated. Count: {len(self.presets)}")

        except ValueError:
            self.error_handler.error(
                f"Preset '{preset_to_delete.name}' not found in internal list for deletion",
                context="Preset deletion"
            )

    @Slot(Preset, str)
    def handle_preset_renamed(self, preset: Preset, new_name: str) -> None:
        """Handle renaming a preset."""
        if preset in self.presets:
            old_name = preset.name
            preset.name = new_name
            get_logger().log(f"Renamed preset '{old_name}' to '{preset.name}'")

            # Save changes to configuration
            self._save_presets_to_config()
        else:
            self.error_handler.error(
                "Preset object not found in internal list for rename",
                context="Preset renaming"
            )

    @Slot(Preset, int)
    def handle_preset_moved(self, preset: Preset, new_index: int) -> None:
        """Handle moving a preset to a new position."""
        if not preset or preset not in self.presets:
            return

        try:
            current_index = self.presets.index(preset)

            # Remove the preset from its current position
            self.presets.pop(current_index)

            # Insert it at the new position, ensuring index is within bounds
            if new_index >= len(self.presets):
                self.presets.append(preset)
            else:
                self.presets.insert(new_index, preset)

            # Save changes to configuration
            self._save_presets_to_config()

        except ValueError:
            self.error_handler.error(
                f"Preset '{preset.name}' not found for moving",
                context="Preset moving"
            )

    @Slot(Preset)
    def handle_preset_start(self, preset: Preset) -> None:
        """Handle starting a preset measurement."""
        get_logger().log(f"Start requested for preset '{preset.name}'")
        self.handle_preset_selection(preset)
        self.run_start.emit(preset)

    @Slot(Preset, Trial)
    def handle_trial_deleted(self, preset: Preset, trial: Trial) -> None:
        """Handle deleting a trial from a preset."""
        trial_type_name = Constants.run_modes[trial.trial_type]
        get_logger().log(f"Deleting trial '{trial_type_name}' from preset")

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the {trial_type_name} trial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            get_logger().log("Trial deletion cancelled by user")
            return

        self.clear_params_tab()

        try:
            was_selected = self.currently_selected_trial == trial
            preset.trials.remove(trial)
            self.trials_column.on_trial_deletion_confirmed(trial)

            # If the deleted item was selected, clear the selection
            if was_selected:
                self.currently_selected_trial = None

            self.trials_column.update_trials(preset)

            # Save changes to configuration
            self._save_presets_to_config()

            get_logger().log(f"Trial list updated. Count: {len(preset.trials)}")

        except ValueError:
            self.error_handler.error(
                f"{trial_type_name} trial not found in preset for deletion",
                context="Trial deletion"
            )

    @Slot(Preset, Trial)
    def handle_trial_created(self, preset: Preset, trial: Trial) -> None:
        """Handle creating a new trial in a preset."""
        get_logger().log(f"Creating new trial '{trial}' in preset '{preset.name}'")

        preset.trials.append(trial)
        self.handle_trial_edit_button(preset, trial)
        self._save_presets_to_config()

        get_logger().log(f"Preset trial list updated. Count: {len(preset.trials)}")

    @Slot(Preset, Trial)
    def handle_trial_edit_button(self, preset: Preset, trial: Trial) -> None:
        """Handle editing a trial's parameters."""
        get_logger().log(f"Editing trial '{trial}' in preset '{preset.name}'")

        self.clear_params_tab(reset=False)

        # Create a new SetupTab with the trial's mode and parameters
        self.param_tab = SetupTab(mode=trial.trial_type, params=trial.params)
        self.param_tab.valueChanged.connect(self.handle_trial_value_edit)

        self.currently_selected_trial = trial
        self.param_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the new widget to the layout
        self.layout.addWidget(self.param_tab, 1)

    @Slot(dict)
    def handle_trial_value_edit(self, params: dict[str, str]) -> None:
        """Handle editing trial parameter values."""
        if not self.currently_selected_trial:
            return

        get_logger().log(f"Updating trial parameters: {params}")
        self.currently_selected_trial.params = params
        self._save_presets_to_config()

    @Slot(Trial, Preset, int)
    def handle_trial_moved(self, trial: Trial, preset: Preset, new_index: int) -> None:
        """Handle moving a trial to a new position within a preset."""
        if not preset or trial not in preset.trials:
            return

        try:
            current_index = preset.trials.index(trial)

            # Remove the trial from its current position
            preset.trials.pop(current_index)

            # Insert it at the new position, ensuring index is within bounds
            if new_index >= len(preset.trials):
                preset.trials.append(trial)
            else:
                preset.trials.insert(new_index, trial)

            # Save changes to configuration
            self._save_presets_to_config()

        except ValueError:
            self.error_handler.error(
                f"Trial not found in preset for moving",
                context="Trial moving"
            )


if __name__ == "__main__":
    """Test the PresetQueueWidget standalone."""
    app = QApplication(sys.argv)

    # Create a test configuration file path
    test_config = "test_userSettings.json"

    window = PresetQueueWidget(test_config)
    window.show()
    sys.exit(app.exec())
