import serial.tools.list_ports
import logging
from typing import Dict, List
log_name = 'arduino_assignment'

arduino_assignments = {"55131323837351A04202": 1,
                        "55139313535351406241": 2}

arduino_assignments_location = {"1-5.4": 1,
                                "1-5.3" : 2,
                                "1-5.1" : 3,
                                "1-5.2" : 4}

def _show_all_com_devices() -> List[serial.tools.list_ports.comports]:
    ports = [
        p
        for p in serial.tools.list_ports.comports()
    ]
    if not ports:
        logging.error('%s No Arduino found', log_name)
        raise IOError()
    return ports

def get_arduino_assignments():
    assigned_arduinos = []
    for device in _show_all_com_devices():
        if (device.location in arduino_assignments_location.keys()):
            assigned_arduinos.append({"ID" : arduino_assignments_location[device.location], "com":device.device})
        # if (("Arduino" in device.description or
        #     "USB Serial Device" in device.description)
        #     and device.serial_number in arduino_assignments):
        #     assigned_arduinos.append({"serial" : arduino_assignments[device.serial_number], "com":device.device})
        # elif "USB-SERIAL CH340" in device.description:
        #     assigned_arduinos.append({"serial" : 3, "com":device.device})
    return assigned_arduinos

if __name__ == '__main__':
    # print(_show_all_com_devices())

    for i in _show_all_com_devices():
        # if "USB-SERIAL CH340" in i.description:
        print(f"Device: {i.device}")
        print(f"Name: {i.name}")
        print(f"Description: {i.description}")
        print(f"Serial Number: {i.serial_number}")
        print(f"Manufacturer: {i.manufacturer}")
        print(f"Product: {i.product}")
        print(f"Vendor ID: {i.vid}")
        print(f"Product ID: {i.pid}")
        print(f"Location: {i.location}")
        print(f"Hardware ID: {i.hwid}")
        print(f"Interface: {i.interface}")
        print()


    print(get_arduino_assignments())

