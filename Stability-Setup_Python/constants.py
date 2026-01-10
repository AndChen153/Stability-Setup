# constants.py
from enum import Enum

class Mode(Enum):
    STOP = 0
    SCAN = 1
    MPPT = 2
    LOGGER = 3
    PLOTTER = 4

class Constants:
    time_param = "Total Time"
    time_unit = "Time Param"
    light_mode_text = "1"
    dark_mode_text = "0"
    scan_mode_param = "Scan Mode"
    mppt_voltage_range_param = "Starting Voltage (V)"
    run_modes = {
        Mode.SCAN: "Scan",
        Mode.MPPT: "Mppt",
    }
    arduino_commands = {
        Mode.SCAN: "scan",
        Mode.MPPT: "mppt",
    }
    arduino_param_translate_scan = {
        "Scan Range (V)":1,
        "Scan Step Size (V)":2,
        "Scan Read Count":3,
        "Scan Rate (mV/s)":4,
        scan_mode_param:5,
    }
    arduino_param_translate_mppt = {
        mppt_voltage_range_param:1,
        "Step Size (V)":2,
        time_param:3,
        "Measurements Per Step":4,
        "Settling Time (ms)":5,
        "Measurement Interval (ms)":6,
    }
    translation_dict = {
        Mode.SCAN : arduino_param_translate_scan,
        Mode.MPPT : arduino_param_translate_mppt,
    }
    run_modes_reversed = {
        "Scan": Mode.SCAN,
        "Mppt": Mode.MPPT,
    }
    params = {
        Mode.SCAN: {
            "Scan Range (V)":"1.2",
            "Scan Step Size (V)":"0.03",
            "Scan Read Count":"10",
            "Scan Rate (mV/s)":"50",
            scan_mode_param:light_mode_text,
            "Cell Area (mm^2)":"0.128",
        },
        Mode.MPPT: {
            "Starting Voltage (V)": "0.50",
            "Starting Voltage Multiplier (%)": "0.85",
            "Step Size (V)": "0.005",
            time_param: "60",
            "Measurements Per Step": "100",
            "Settling Time (ms)": "300",
            "Measurement Interval (ms)": "200",
            "Cell Area (mm^2)": "0.128",
            time_unit: "mins"
       },
    }
    line_per_save = 20
    unknown_Arduino_ID = -1
