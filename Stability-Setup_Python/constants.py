from enum import Enum

class Mode(Enum):
    STOP = 0
    SCAN = 1
    MPPT = 2
    PLOTTER = 4

class UI_Mode(Enum):
    SCAN = 1
    MPPT = 2

class ConstantsGUI:
    pages = {
        Mode.SCAN: "Scan",
        Mode.MPPT: "MPPT",
        Mode.PLOTTER: "Graph Viewer",

    }
    params = {
        Mode.SCAN: [
            "Trial Name",
            "Scan Range (V):",
            "Scan Step Size (V):",
            "Scan Read Count:",
            "Scan Rate (mV/s):",
            "Scan Mode(dark, light):",
        ],
        Mode.MPPT: [
            "Trial Name",
            "Starting Voltage (V):",
            "Step Size (V):",
            "Measurements Per Step:",
            "Measurement Delay (ms):",
            "Time (mins):",
            "Cell Area (mm^2):"
        ],
        Mode.PLOTTER: ["Data Location"],
    }
    defaults = {
        Mode.SCAN: ["", "1.2", "0.03", "5", "50", "1"],
        Mode.MPPT: ["", "0.50", "0.01", "5", "300", "60", "0.128"],
        Mode.PLOTTER: [""],
    }
    plotModes = [Mode.PLOTTER]

class ConstantsController:
    save_time = 5
    serial_baud_rate = 115200
    arduino_ID = {"F05123D": 1}