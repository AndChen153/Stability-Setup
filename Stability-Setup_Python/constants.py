from enum import Enum

class Mode(Enum):
    STOP = 0
    SCAN = 1
    PNO = 2
    CONSTANT = 3

class UI_Mode(Enum):
    SCAN = 1
    PNO = 2
    CONSTANT = 3

constants_gui = {
    "pages": {Mode.SCAN: "Scan", Mode.PNO: "PNO", Mode.CONSTANT: "Constant Voltage"},
    "params": {
        Mode.SCAN: [
            "Scan Range (V):",
            "Scan Step Size (V):",
            "Scan Read Count:",
            "Scan Rate (mV/s):",
            "Scan Mode(dark, light):",
        ],
        Mode.PNO: [
            "PNO Starting Voltage (V):",
            "PNO Step Size (V):",
            "PNO Measurements Per Step:",
            "PNO Measurement Delay (ms):",
            "Time (mins):",
        ],
        Mode.CONSTANT: ["Constant Voltage (V):"],
    },
    "defaults": {
        Mode.SCAN: ["1.2", "0.03", "5", "50", "1"],
        Mode.PNO: ["0.50", "0.01", "5", "300", "60"],
        Mode.CONSTANT: ["0.5"],
    },
}

constants_controller = {
    "save_time" : 5,
    "serial_baud_rate" : 115200,
}