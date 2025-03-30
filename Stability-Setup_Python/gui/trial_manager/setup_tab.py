# gui/setup_tab.py
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox
)
from PySide6.QtCore import Signal
from constants import Mode, Constants

class SetupTab(QWidget):
    # Signals to notify the parent (MainWindow) when a run or stop is requested.
    runRequested = Signal(object, list)   # emits (mode, params)
    stopRequested = Signal(object)          # emits mode

    def __init__(self, mode, parent=None):
        """
        :param mode: The mode (from Constants) for which this tab is built.
        """
        super().__init__(parent)
        self.mode = mode
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
            params = Constants.params[self.mode]
            defaults = Constants.defaults.get(
                self.mode, [""] * len(params)
            )
            for param, default in zip(params, defaults):
                if param == Constants.time_param:
                    # Build a container for time (with Mins/Hrs buttons)
                    container = QWidget()
                    h_layout = QHBoxLayout(container)
                    h_layout.setContentsMargins(0, 0, 0, 0)

                    mins_button = QPushButton("Mins")
                    hrs_button = QPushButton("Hrs")
                    time_line_edit = QLineEdit()
                    time_line_edit.setText(default)

                    h_layout.addWidget(mins_button)
                    h_layout.addWidget(hrs_button)
                    h_layout.addWidget(time_line_edit)

                    self.mppt_time_unit = "mins"
                    self.mppt_time_line_edit = time_line_edit
                    self.mppt_mins_button = mins_button
                    self.mppt_hrs_button = hrs_button

                    mins_button.setEnabled(False)
                    mins_button.clicked.connect(self.switch_to_minutes)
                    hrs_button.clicked.connect(self.switch_to_hours)
                    time_line_edit.textChanged.connect(self.update_estimated_data_amount)

                    form_layout.addRow(param, container)
                    self.textboxes.append((param, time_line_edit))
                elif self.mode == Mode.SCAN and param == "Scan Mode":
                    # Build a toggle button for scan mode
                    self.toggle_button = QPushButton()
                    self.toggle_button.setCheckable(True)
                    self.toggle_button.setText(default)
                    if default.lower() == Constants.dark_mode_text:
                        self.toggle_button.setChecked(True)
                    else:
                        self.toggle_button.setChecked(False)
                    self.toggle_button.clicked.connect(self.toggle_scan_mode)
                    form_layout.addRow(param, self.toggle_button)
                    self.textboxes.append((param, self.toggle_button))
                else:
                    # Standard parameter field
                    line_edit = QLineEdit()
                    line_edit.setText(default)
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
        else:
            form_layout.addRow(QLabel("No parameters defined for this mode."))

        # --- Run and Stop Buttons ---
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(lambda: self.stopRequested.emit(self.mode))
        button_layout.addWidget(self.stop_button)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.handle_run)
        button_layout.addWidget(self.run_button)
        form_layout.addRow(QWidget(), button_container)

        layout.addLayout(form_layout)
        self.update_buttons()

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
                estimated = Constants.kbPerDataPoint * Time_s / (Delay_s + 0.1)
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
            current_value = float(self.mppt_time_line_edit.text())
            new_value = int(current_value * 60)
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "mins"
            self.mppt_mins_button.setEnabled(False)
            self.mppt_hrs_button.setEnabled(True)
            self.update_estimated_data_amount()
        except ValueError:
            pass

    def switch_to_hours(self):
        """Switch the time unit to hours."""
        if self.mppt_time_unit == "hrs":
            return
        try:
            current_value = float(self.mppt_time_line_edit.text())
            new_value = current_value / 60
            self.mppt_time_line_edit.setText(str(new_value))
            self.mppt_time_unit = "hrs"
            self.mppt_hrs_button.setEnabled(False)
            self.mppt_mins_button.setEnabled(True)
            self.update_estimated_data_amount()
        except ValueError:
            pass

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
        params = []
        for param, widget in self.textboxes:
            if param == Constants.time_param:
                time_text = widget.text()
                if self.mppt_time_unit == "hrs":
                    Time_m = int(float(time_text)) * 60 if time_text else 0.0
                else:
                    Time_m = int(float(time_text)) if time_text else 0.0
                params.append(str(Time_m))
            elif self.mode == Mode.SCAN and param == "Scan Mode":
                # Toggle state: checked means "0", unchecked means "1"
                if self.toggle_button.isChecked():
                    params.append("0")
                else:
                    params.append("1")
            else:
                params.append(widget.text())
        # Emit the run request with the collected parameters.
        self.runRequested.emit(self.mode, params)
        # Update buttons to reflect that a run is in progress.
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
