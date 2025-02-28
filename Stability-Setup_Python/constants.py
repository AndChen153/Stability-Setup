# constants.py
from enum import Enum


class Mode(Enum):
    STOP = 0
    SCAN = 1
    MPPT = 2
    LOGGER = 3
    PLOTTER = 4

class Constants:
    timeParam = "Measurement Time"
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
            "Scan Mode",
        ],
        Mode.MPPT: [
            "Starting Voltage (V)",
            "Step Size (V)",
            "Cell Area (mm^2)",
            "Measurements Per Step",
            "Measurement Delay (ms)",
            timeParam,
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
            "light",
        ],
        Mode.MPPT: [
            "0.50",
            "0.01",
            "0.128",
            "5",
            "300",
            "60",
        ],
        Mode.PLOTTER: [""],
    }
    recommended_values = {
        Mode.SCAN: [
            (0, 3.3),
            (0.0001, 0.1),
            (0, 1000),
            (2, 10),
            (25, 100),
            (0, 1),
        ],
        Mode.MPPT: [
            (0.1, 1.5),
            (0.005, 0.1),
            (0, 1000),
            (2, 10),
            (50, 2000),
            (1, 600000),
        ],
    }
    plotModes = [Mode.PLOTTER]
    line_per_save = 15
    serial_baud_rate = 115200
    kbPerDataPoint = 0.15
    gbCalculationParams = ["Measurement Delay (ms)", timeParam]
    unknown_Arduino_ID = -1
    warning_precursor = "Some of your values are outside of the recommended ranges, running a trial with these values may result in the program crashing or not performing as expected. Press Continue if you would like to proceed. \n"
