import json
import os
from constants import Constants, Mode
from helper.global_helpers import get_logger
from PySide6.QtWidgets import QComboBox
from gui.trial_manager.preset_data_class import Preset, Trial

class PresetManager:
    def __init__(self, preset_file_path):
        """
        preset_file: Path to the centralized JSON file containing all settings.
        """
        self.preset_file_path = preset_file_path
        self.data = None

    def load_presets_from_json(self):
        """
        Loads preset data from a JSON file into a list of Preset objects.

        :param filepath: Path to the JSON file.
        :return: A list of Preset objects.
        :raises FileNotFoundError: If the filepath does not exist.
        :raises json.JSONDecodeError: If the file is not valid JSON.
        :raises KeyError: If the 'presets' key is missing in the JSON root.
        :raises TypeError: If the data structure within 'presets' is incorrect.
        :raises ValueError: If a trial definition is invalid (e.g., wrong param count).
        """
        try:
            with open(self.preset_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found at {self.preset_file_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON from {self.preset_file_path}. Details: {e}")
            raise

        if "presets" not in data:
            raise KeyError("The JSON data must contain a 'presets' key.")
        self.data = data
        presets_data = data["presets"]
        if not isinstance(presets_data, dict):
            raise TypeError("Expected 'presets' to be a dictionary (object) in JSON.")

        loaded_presets = []

        for ID, data in presets_data.items():
            trial_name = data["trial_name"]
            trials = data["trial"]

            trials_populated = []

            for trial in trials:
                trial_type = Constants.run_modes_reversed[trial["trial_type"]]
                trial_id = trial["trial_id"]
                trial_params = trial["trial_params"]
                trials_populated.append(Trial(trial_type, trial_params, trial_id))

            loaded_presets.append(Preset(trial_name, ID, trials_populated))

        return loaded_presets

    def save_presets_to_json(self , all_presets):
        """
        Saves a list of Preset objects to a JSON file, updating the 'presets' key.

        :param all_presets: A list of Preset objects to save.
        :param existing_data: The dictionary loaded from the JSON file (or an empty
                            dict if the file didn't exist/was invalid). This is
                            used to preserve other top-level keys.
        :raises TypeError: If all_presets is not a list or contains non-Preset objects.
        :raises IOError: If there's an error writing the file.
        """
        if not isinstance(all_presets, list):
            raise TypeError("Input 'all_presets' must be a list.")

        # referesh data
        self.load_presets_from_json()
        presets_data = {str(p.id): self.preset_to_dict(p) for p in all_presets}
        self.data["presets"] = presets_data
        with open(self.preset_file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def preset_to_dict(self, preset: Preset) -> dict:
        """
        Convert a Preset instance into a dictionary.
        The resulting dictionary contains the preset name under 'trial_name'
        and a list of trial dictionaries under 'trial'.
        """
        return {
            "trial_name": preset.name,
            "trial": [self.trial_to_dict(t) for t in preset.trials]
        }

    def trial_to_dict(self, trial: Trial) -> dict:
        """
        Convert a Trial instance into a dictionary matching the JSON format.
        """
        return {
            "trial_type": Constants.run_modes[trial.trial_type],
            "trial_id" : str(trial.id),
            "trial_params": trial.params
        }
