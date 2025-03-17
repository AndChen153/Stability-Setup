# constants.py
from enum import Enum


class Mode(Enum):
    STOP = 0
    SCAN = 1
    MPPT = 2
    LOGGER = 3
    PLOTTER = 4

class Constants:
    time_param = "Measurement Time"
    light_mode_text = "Light"
    dark_mode_text = "Dark"
    scan_mode_param = "Scan Mode"
    pages = {
        Mode.SCAN: "Scan",
        Mode.MPPT: "MPPT",
        Mode.PLOTTER: "Graph Viewer",
        Mode.LOGGER: "Log Viewer"
    }
    right_modes = [Mode.PLOTTER, Mode.LOGGER]
    left_modes = [Mode.SCAN, Mode.MPPT]
    common_params = ["Trial Name", "Email for Notification"]
    common_defaults = ["", ""]
    params = {
        Mode.SCAN: [
            "Scan Range (V)",
            "Scan Step Size (V)",
            "Cell Area (mm^2)",
            "Scan Read Count",
            "Scan Rate (mV/s)",
            scan_mode_param,
        ],
        Mode.MPPT: [
            "Starting Voltage (V)",
            "Step Size (V)",
            "Cell Area (mm^2)",
            "Measurements Per Step",
            "Measurement Delay (ms)",
            time_param,
        ],
        Mode.PLOTTER: ["Data Location"],
    }
    defaults = {
        Mode.SCAN: [
            "1.2",
            "0.03",
            "0.128",
            "5",
            "50",
            light_mode_text,
        ],
        Mode.MPPT: [
            "0.50",
            "0.005",
            "0.128",
            "10",
            "1000",
            "60",
        ],
        Mode.PLOTTER: [""],
    }
    recommended_values = {
        Mode.SCAN: [
            (0, 3.3),
            (0.001, 0.1),
            (0, 1000),
            (5, 10),
            (25, 100),
            (0, 1),
        ],
        Mode.MPPT: [
            (0.1, 1.5),
            (0.001, 0.02),
            (0, 1000),
            (10, 20),
            (500, 2000),
            (1, 600000),
        ],
    }
    plotModes = [Mode.PLOTTER]
    line_per_save = 20
    serial_baud_rate = 115200
    kbPerDataPoint = 0.15
    gbCalculationParams = ["Measurement Delay (ms)", time_param]
    unknown_Arduino_ID = -1
    warning_precursor = "Some of your values are outside of the recommended ranges, running a trial with these values may result in the program crashing or not performing as expected. Press Continue if you would like to proceed. \n"
