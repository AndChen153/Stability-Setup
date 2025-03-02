from PySide6.QtWidgets import QMessageBox
from constants import Mode, Constants

class PopupNotificationBase:
    def __init__(self, parent=None, title="", message="",
                 icon=QMessageBox.Information, buttons=QMessageBox.Ok | QMessageBox.Cancel):
        self.parent = parent
        self.title = title
        self.message = message
        self.icon = icon
        self.buttons = buttons
        self.skip_warning = False

    def exec_(self):
        if self.skip_warning:
            return True
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(self.icon)
        msg_box.setText(self.message)
        msg_box.setWindowTitle(self.title)
        msg_box.setStandardButtons(self.buttons)
        self.customize(msg_box)
        if msg_box.exec() == QMessageBox.Ok:
            return True
        return False

    def customize(self, msg_box: QMessageBox):
        pass

class SelectionPopup(PopupNotificationBase):
    def __init__(self, parent=None, title="", message="", current_values=None, mode=None, **kwargs):
        # Call the superclass initializer with remaining arguments.
        super().__init__(parent=parent, title=title, message=message, **kwargs)
        self.current_values = current_values
        self.mode = mode

        self.outside_param = []
        self.outside_value = []
        self.outside_range = []

        for param_name, value, recommended_range in zip(Constants.params[self.mode],
                                                        self.current_values,
                                                        Constants.recommended_values[self.mode]):
            if self.is_outside_range(float(value), recommended_range):
                self.outside_param.append(param_name)
                self.outside_value.append(value)
                self.outside_range.append(recommended_range)

        if not self.outside_range:
            self.skip_warning = True

    def customize(self, msg_box: QMessageBox):
        # Change the OK button to display "Continue" instead.
        warning_strings = [Constants.warning_precursor]
        for param_name, value, recommended_range in zip(self.outside_param,
                                                        self.outside_value,
                                                        self.outside_range):
            warning_strings.append(f"{param_name} value of {value} outside of recommended range of {recommended_range}.")
        warning_string = "\n".join(warning_strings)
        msg_box.setText(warning_string)
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setText("Continue")

    def is_outside_range(self, value, range_tuple):
        low, high = range_tuple
        return value < low or value > high