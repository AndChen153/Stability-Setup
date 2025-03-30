class Trial:
    def __init__(self, trial_type, params):
        """
        :param trial_type: A string, e.g. "Scan" or "mppt"
        :param params: A list of 6 string parameters.
        """
        if len(params) != 6:
            raise ValueError("Expected 6 parameter values")
        self.trial_type = trial_type
        self.params = params

    def __repr__(self):
        return f"Trial({self.trial_type}, {self.params})"


class Preset:
    def __init__(self, name, trials=None):
        """
        :param name: Name of the preset, e.g. "preset1"
        :param trials: A list of Trial objects.
        """
        self.name = name
        self.trials = trials if trials is not None else []

    def add_trial(self, trial):
        self.trials.append(trial)

    def __repr__(self):
        return f"Preset({self.name}, {self.trials})"

if __name__ == "__main__":
    # Example data:
    preset1 = Preset("preset1", [
        Trial("Scan", ["scan1", "scan2", "scan3", "scan4", "scan5", "scan6"]),
        Trial("mppt", ["mppt1", "mppt2", "mppt3", "mppt4", "mppt5", "mppt6"]),
        Trial("Scan", ["scanA", "scanB", "scanC", "scanD", "scanE", "scanF"]),
    ])

    preset2 = Preset("preset2", [
        Trial("Scan", ["s1", "s2", "s3", "s4", "s5", "s6"]),
        Trial("mppt", ["m1", "m2", "m3", "m4", "m5", "m6"]),
    ])

    # Store all presets in a list (or dictionary if you prefer keyed access)
    presets = [preset1, preset2]

    # Print the data to verify
    for p in presets:
        print(p)
