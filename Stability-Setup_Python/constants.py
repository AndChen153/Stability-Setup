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
    pages = {
        Mode.SCAN: "Scan",
        Mode.MPPT: "MPPT",
        Mode.PLOTTER: "Graph Viewer",
    }
    params = {
        Mode.SCAN: [
            "Trial Name",
            "Scan Range (V)",
            "Scan Step Size (V)",
            "Cell Area (mm^2)",
            "Scan Read Count",
            "Scan Rate (mV/s)",
            "Scan Mode(dark = 0/light = 1)",
        ],
        Mode.MPPT: [
            "Trial Name",
            "Starting Voltage (V)",
            "Step Size (V)",
            "Cell Area (mm^2)",
            "Measurements Per Step",
            "Measurement Delay (ms)",
            "Time (mins)",
        ],
        Mode.PLOTTER: ["Data Location"],
    }
    defaults = {
        Mode.SCAN: [
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
    save_time = 5
    serial_baud_rate = 115200
    arduino_ID = {"F05123D": 1}
