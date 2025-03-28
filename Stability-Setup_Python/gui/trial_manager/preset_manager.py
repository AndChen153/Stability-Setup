import json
import os
from constants import Constants, Mode
from helper.global_helpers import custom_print
from PySide6.QtWidgets import QComboBox

class PresetManager:
    def __init__(self, preset_file, textboxes, preset_dropdown, popup_callback):
        """
        preset_file: Path to the centralized JSON file containing all settings.
        textboxes: Dictionary keyed by Mode; value is a list of tuples (param, widget)
        preset_dropdown: Dictionary keyed by Mode; value is the QComboBox for that mode.
        popup_callback: Function to display popup messages (e.g. main window's show_popup).
        """
        self.preset_file = preset_file
        self.textboxes = textboxes
        self.preset_dropdown = preset_dropdown
        self.popup_callback = popup_callback

    def populate_all(self):
        for mode in self.preset_dropdown.keys():
            self.populate_dropdown(mode)

    def _load_file(self):
        if os.path.exists(self.preset_file):
            with open(self.preset_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}
        return data

    def _load_presets(self):
        data = self._load_file()
        presets = data.get("presets", {})
        return presets

    def _save_presets(self, presets):
        data = self._load_file()
        data["presets"] = presets
        with open(self.preset_file, "w") as f:
            json.dump(data, f, indent=4)

    def save_preset(self, mode: Mode):
        trial_name = None
        for param, textbox in self.textboxes.get(mode, []):
            if param == "Trial Name":
                trial_name = textbox.text().strip()
                break
        if not trial_name:
            self.popup_callback("Trial Name is required to save a preset.")
            return

        presets = self._load_presets()

        preset_for_mode = {}
        for param, textbox in self.textboxes.get(mode, []):
            preset_for_mode[param] = textbox.text()
        if mode.name not in presets:
            presets[mode.name] = {}
        presets[mode.name][trial_name] = preset_for_mode

        self._save_presets(presets)
        custom_print(f"Preset '{trial_name}' saved for {Constants.run_modes.get(mode, 'Unknown')} mode.")
        self.populate_dropdown(mode)

    def delete_preset(self, mode: Mode):
        trial_name = None
        for param, textbox in self.textboxes.get(mode, []):
            if param == "Trial Name":
                trial_name = textbox.text().strip()
                break
        if not trial_name:
            self.popup_callback("Trial Name is required to delete a preset.")
            return

        presets = self._load_presets()
        if mode.name in presets and trial_name in presets[mode.name]:
            del presets[mode.name][trial_name]
            self._save_presets(presets)
            custom_print(f"Preset '{trial_name}' deleted for {Constants.run_modes.get(mode, 'Unknown')} mode.")
            self.populate_dropdown(mode)
        else:
            self.popup_callback(f"Preset '{trial_name}' not found for {Constants.run_modes.get(mode, 'Unknown')} mode.")

    def populate_dropdown(self, mode: Mode):
        presets = self._load_presets()
        presets_for_mode = presets.get(mode.name, {})
        dropdown: QComboBox = self.preset_dropdown.get(mode)
        if not dropdown:
            return
        else:
            dropdown.blockSignals(True)
            dropdown.clear()
            dropdown.addItem("Select Preset")
            for trial_name in presets_for_mode.keys():
                dropdown.addItem(trial_name)
            dropdown.blockSignals(False)

    def preset_selected(self, mode: Mode):
        dropdown: QComboBox = self.preset_dropdown.get(mode)
        if dropdown:
            trial_name = dropdown.currentText()
            if trial_name == "Select Preset":
                return
            presets = self._load_presets()
            presets_for_mode = presets.get(mode.name, {})
            preset = presets_for_mode.get(trial_name)
            if preset:
                for param, textbox in self.textboxes.get(mode, []):
                    if param in preset:
                        textbox.setText(preset[param])
                custom_print(f"Preset '{trial_name}' loaded for {Constants.run_modes.get(mode, 'Unknown')} mode.")
