# gui/setup_tab.py
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox
)
from PySide6.QtCore import Signal
from constants import Mode, Constants
from helper.global_helpers import logger

kbPerDataPoint = 0.2

class SetupTab(QWidget):
    # Signals to notify the parent (MainWindow) when a run or stop is requested.
    valueChanged = Signal(dict)
    def __init__(self, mode:Mode, params: dict[str, str], parent=None):
        """
        :param mode: The mode (from Constants) for which this tab is built.
        """
        super().__init__(parent)
        if not Mode:
            return
        self.mode = mode
        self.initial_params = params
        self.textboxes = []  # List of tuples: (parameter name, widget)
        self.run_button = None
        self.stop_button = None

        # Attributes used only for MPPT mode:
        self.mppt_time_unit = "mins"
        self.mppt_time_line_edit = None
        self.mppt_mins_button = None
        self.mppt_hrs_button = None
        self.mppt_estimated_gb = None

        # For Scan mode:
        self.toggle_button = None

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Build Parameter Fields ---
        if self.mode in Constants.params:
            if self.initial_params:
                params = self.initial_params
            else:
                params = Constants.params[self.mode]

            for idx, param in enumerate(Constants.params[self.mode]):
                box_value = params[param]
                if param == Constants.time_param:
                    # Build a container for time (with Mins/Hrs buttons)
                    container = QWidget()
                    h_layout = QHBoxLayout(container)
                    h_layout.setContentsMargins(0, 0, 0, 0)

                    mins_button = QPushButton("Mins")
                    hrs_button = QPushButton("Hrs")

                    button_width = 35
                    mins_button.setFixedWidth(button_width)
                    hrs_button.setFixedWidth(button_width)
                    time_line_edit = QLineEdit()


                    h_layout.addWidget(mins_button)
                    h_layout.addWidget(hrs_button)
                    h_layout.addWidget(time_line_edit)

                    self.mppt_time_line_edit = time_line_edit
                    self.mppt_mins_button = mins_button
                    self.mppt_hrs_button = hrs_button

                    if params[Constants.time_unit] == "mins":
                        self.mppt_time_unit = "mins"
                        mins_button.setEnabled(False)
                        time_line_edit.setText(box_value)
                    elif params[Constants.time_unit] == "hrs":
                        self.mppt_time_unit = "hrs"
                        hrs_button.setEnabled(False)
                        hours = float(box_value)/60
                        time_line_edit.setText(str(hours))
                    else:
                        raise KeyError("Unknown time unit for MPPT")
                    mins_button.clicked.connect(self.switch_to_minutes)
                    hrs_button.clicked.connect(self.switch_to_hours)
                    time_line_edit.textChanged.connect(self.update_estimated_data_amount)

                    form_layout.addRow(param, container)
                    time_line_edit.textChanged.connect(self.handle_run)
                    self.textboxes.append((param, time_line_edit))
                elif self.mode == Mode.SCAN and param == "Scan Mode":
                    #TODO: fix this
                    # Build a toggle button for scan mode
                    self.toggle_button = QPushButton()
                    self.toggle_button.setCheckable(True)
                    self.toggle_button.setText("Light On")
                    if box_value == "1":
                        self.toggle_button.setChecked(True)
                    else:
                        self.toggle_button.setChecked(False)
                    self.toggle_button.clicked.connect(self.toggle_scan_mode)
                    form_layout.addRow(param, self.toggle_button)
                    self.textboxes.append((param, self.toggle_button))
                elif param == Constants.time_unit:
                    continue
                else:
                    # Standard parameter field
                    line_edit = QLineEdit()
                    line_edit.setText(box_value)
                    line_edit.textChanged.connect(self.handle_run)
                    form_layout.addRow(param, line_edit)
                    self.textboxes.append((param, line_edit))


            # For MPPT mode, add the estimated data amount field.
            if self.mode == Mode.MPPT:
                self.mppt_estimated_gb = QLineEdit()
                self.mppt_estimated_gb.setReadOnly(True)
                self.mppt_estimated_gb.setText("0.0")
                self.mppt_estimated_gb.setStyleSheet("QLineEdit { border: none; background-color: transparent; }")
                self.update_estimated_data_amount()
                form_layout.addRow("Estimated Data Amount", self.mppt_estimated_gb)

        layout.addLayout(form_layout)
        # self.update_buttons()

    def update_estimated_data_amount(self):
        """Compute and update the estimated data amount based on time and delay."""
        time_text = None
        delay_text = None
        for param, widget in self.textboxes:
            if param == Constants.time_param:
                time_text = widget.text()
            elif param == "Measurement Delay (ms)":
                delay_text = widget.text()
        try:
            if self.mppt_time_unit == "hrs":
                Time_s = float(time_text) * 3600 if time_text else 0.0
            else:
                Time_s = float(time_text) * 60 if time_text else 0.0
            Delay_s = float(delay_text) / 1000 if delay_text else 0.0
            if Delay_s == 0:
                estimated = 0.0
            else:
                estimated = kbPerDataPoint * Time_s / (Delay_s + 0.1)
            unit = "kb"
            if estimated > 1000000:
                estimated = estimated / 1000000
                unit = "gb"
            elif estimated > 1000:
                estimated = estimated / 1000
                unit = "mb"
            estimated = round(estimated, 2)
            if self.mppt_estimated_gb:
                self.mppt_estimated_gb.setText(f"{estimated} {unit}")
        except ValueError:
            if self.mppt_estimated_gb:
                self.mppt_estimated_gb.setText("Error")

    def switch_to_minutes(self):
        """Switch the time unit to minutes."""
        if self.mppt_time_unit == "mins":
            return
        try:
            # current_value = float(self.mppt_time_line_edit.text())
            # new_value = int(current_value * 60)
            # self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "mins"
            self.mppt_mins_button.setEnabled(False)
            self.mppt_hrs_button.setEnabled(True)
            self.update_estimated_data_amount()
            self.handle_run()
        except ValueError:
            pass

        logger.log("Switched to mins", self.mppt_time_unit, self.mppt_time_line_edit)

    def switch_to_hours(self):
        """Switch the time unit to hours."""
        if self.mppt_time_unit == "hrs":
            return
        try:
            # current_value = float(self.mppt_time_line_edit.text())
            # new_value = current_value / 60
            # self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "hrs"
            self.mppt_hrs_button.setEnabled(False)
            self.mppt_mins_button.setEnabled(True)
            self.update_estimated_data_amount()
            self.handle_run()
        except ValueError:
            pass

        logger.log("Switched to hrs", self.mppt_time_unit, self.mppt_time_line_edit)


    def update_buttons(self):
        """Update button enabled/disabled states (for now, run enabled and stop disabled)."""
        if self.run_button:
            self.run_button.setEnabled(True)
        if self.stop_button:
            self.stop_button.setEnabled(False)

    def toggle_scan_mode(self):
        """Toggle the scan mode between light and dark mode."""
        if self.toggle_button.text().lower() == Constants.light_mode_text:
            self.toggle_button.setText(Constants.dark_mode_text)
            self.toggle_button.setChecked(True)
        else:
            self.toggle_button.setText(Constants.light_mode_text)
            self.toggle_button.setChecked(False)

    def handle_run(self):
        """
        Gather all parameters from the UI and emit the runRequested signal.
        The parent (MainWindow) should handle the actual measurement logic.
        """
        params = {}
        for param, widget in self.textboxes:
            if param == Constants.time_param:
                logger.log(param, widget.text(), self.mppt_time_unit)
                time_text = widget.text()
                if self.mppt_time_unit == "hrs":
                    Time_m = int(float(time_text)) * 60 if time_text else 0.0
                else:
                    Time_m = int(float(time_text)) if time_text else 0.0
                params[param] = str(Time_m)
                params[Constants.time_unit] = self.mppt_time_unit
            elif self.mode == Mode.SCAN and param == "Scan Mode":
                # Toggle state: checked means "0", unchecked means "1"
                if self.toggle_button.isChecked():
                    params[param] = "0"
                else:
                    params[param] = "1"
            else:
                params[param] = widget.text()

        self.valueChanged.emit(params)
