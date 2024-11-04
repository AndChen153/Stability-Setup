from enum import Enum

class Page(Enum):
    SCAN = 1
    PNO = 2
    CONSTANT = 3

constants = {
    "pages": {Page.SCAN: "Scan", Page.PNO: "PNO", Page.CONSTANT: "Constant Voltage"},
    "params": {
        Page.SCAN: [
            "Scan Range (V):",
            "Scan Step Size (V):",
            "Scan Read Count:",
            "Scan Rate (mV/s):",
            "Scan Mode(dark, light):",
        ],
        Page.PNO: [
            "PNO Starting Voltage (V):",
            "PNO Step Size (V):",
            "PNO Measurements Per Step:",
            "PNO Measurement Delay (ms):",
            "Time (mins):",
        ],
        Page.CONSTANT: ["Constant Voltage (V):"],
    },
    "defaults": {
        Page.SCAN: ["1.2", "0.03", "5", "50", "1"],
        Page.PNO: ["0.90", "0.02", "5", "100", "600"],
        Page.CONSTANT: ["0.5"],
    },
}
