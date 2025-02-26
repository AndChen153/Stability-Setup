# constants.py
from enum import Enum


class Mode(Enum):
    STOP = 0
    SCAN = 1
    MPPT = 2
    PLOTTER = 4


class UI_Mode(Enum):
    SCAN = 1
    MPPT = 2


class Constants:
    timeParam = "Measurement Time"
    pages = {
        Mode.SCAN: "Scan",
        Mode.MPPT: "MPPT",
        Mode.PLOTTER: "Graph Viewer",
    }
    common_params = ["Trial Name", "Email for Notification"]
    params = {
        Mode.SCAN: common_params
        + [
            "Scan Range (V)",
            "Scan Step Size (V)",
            "Cell Area (mm^2)",
            "Scan Read Count",
            "Scan Rate (mV/s)",
            "Scan Mode(dark = 0/light = 1)",
        ],
        Mode.MPPT: common_params
        + [
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
            "",
            "",
            "1.2",
            "0.03",
            "0.128",
            "5",
            "50",
            "1",
        ],
        Mode.MPPT: [
            "",
            "",
            "0.50",
            "0.01",
            "0.128",
            "5",
            "300",
            "60",
        ],
        Mode.PLOTTER: [""],
    }
    plotModes = [Mode.PLOTTER]
    line_per_save = 15
    serial_baud_rate = 115200
    arduino_ID = {"F05123D": 1}
    kbPerDataPoint = 0.15
    gbCalculationParams = ["Measurement Delay (ms)", timeParam]
