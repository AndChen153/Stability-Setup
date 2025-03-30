import json
import os
from constants import Constants, Mode
from helper.global_helpers import custom_print
from PySide6.QtWidgets import QComboBox
from gui.trial_manager.preset_data_class import Preset, Trial

class PresetManager:
    def __init__(self, preset_file_path):
        """
        preset_file: Path to the centralized JSON file containing all settings.
        """
        self.preset_file_path = preset_file_path

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

        presets_data = data["presets"]
        if not isinstance(presets_data, dict):
            raise TypeError("Expected 'presets' to be a dictionary (object) in JSON.")

        loaded_presets = []

        for preset_name, trials_list_data in presets_data.items():
            if not isinstance(trials_list_data, list):
                print(f"Warning: Expected a list of trials for preset '{preset_name}', but got {type(trials_list_data)}. Skipping this preset.")
                continue

            current_trials = []
            for i, trial_dict in enumerate(trials_list_data):
                if not isinstance(trial_dict, dict):
                    print(f"Warning: Expected trial definition {i+1} in preset '{preset_name}' to be a dictionary, but got {type(trial_dict)}. Skipping this trial.")
                    continue
                if len(trial_dict) != 1:
                    print(f"Warning: Trial definition {i+1} in preset '{preset_name}' should have exactly one key (trial type), but found {len(trial_dict)} keys: {list(trial_dict.keys())}. Skipping this trial.")
                    continue

                # Extract the single key (trial_type) and its value (params)
                trial_type = list(trial_dict.keys())[0]
                params = trial_dict[trial_type]

                try:
                    # Create the Trial object (validation happens inside __init__)
                    trial_obj = Trial(trial_type, params)
                    current_trials.append(trial_obj)
                except (ValueError, TypeError) as e:
                    print(f"Error creating Trial {i+1} ('{trial_type}') for preset '{preset_name}': {e}. Skipping this trial.")
                    # Optionally re-raise if you want loading to fail completely
                    # raise ValueError(f"Invalid trial data for preset '{preset_name}', trial {i+1}: {e}") from e

            # Create the Preset object with the collected trials
            preset_obj = Preset(preset_name, current_trials)
            loaded_presets.append(preset_obj)

        return loaded_presets


    def save_presets_to_json(self , all_presets, existing_data):
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

        presets_data_to_save = {}
        for preset in all_presets:
            if not isinstance(preset, Preset):
                raise TypeError(f"Item in 'all_presets' is not a Preset object: {preset}")
            # Use the helper method in Preset class to get the correct trial format
            presets_data_to_save[preset.name] = preset.trials_to_list_of_dicts()

        # Update the 'presets' key in the existing data structure
        # This preserves other keys like 'arduino_ids', 'email_settings'
        data_to_write = existing_data.copy() # Avoid modifying the original dict if passed elsewhere
        data_to_write["presets"] = presets_data_to_save

        # Write the updated data structure back to the JSON file
        try:
            with open(self.preset_file_path, 'w') as f:
                # Use indent=4 for pretty printing, matching the original format
                json.dump(data_to_write, f, indent=4)
            print(f"Successfully saved presets to {self.preset_file_path}")
        except IOError as e:
            print(f"Error: Could not write presets to file {self.preset_file_path}. Details: {e}")
            raise # Re-raise the exception so the caller knows saving failed
        except TypeError as e:
            # This might happen if data_to_write contains non-serializable objects,
            # though unlikely with this structure.
            print(f"Error: Could not serialize data for JSON writing. Details: {e}")
            raise
