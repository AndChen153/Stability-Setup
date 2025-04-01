import uuid
from constants import Mode, Constants

class Trial:
    def __init__(self, trial_type:Mode, params: list[str], id = None):
        """
        :param trial_type: A string, e.g. "Scan" or "mppt"
        :param params: A list of string parameters.
        """
        self.trial_type:Mode = trial_type
        self.params = params
        self.id = id if id else uuid.uuid4() # Unique ID per Trial

    # Optional: For easier comparison/removal if needed
    def __eq__(self, other):
        if not isinstance(other, Trial):
            return NotImplemented
        return self.id == other.id

    def __repr__(self):
        return f"Trial({self.trial_type}, {self.params})"

class Preset:
    def __init__(self, name: str, id = None, trials: list[Trial] = None):
        self.name = name
        self.trials = trials if trials else []
        self.id = id if id else uuid.uuid4() # Unique ID per preset

    # Optional: For easier comparison/removal if needed
    def __eq__(self, other):
        if not isinstance(other, Preset):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Preset(id={self.id}, name='{self.name}', trials={len(self.trials)})"
