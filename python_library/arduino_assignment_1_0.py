import serial.tools.list_ports
import logging
from typing import Dict, List
log_name = 'arduino_assignment'

arduino_assignments = {"7513131393235191E0E1": 0,
                        "55139313535351406241": 1}

def _show_all_com_devices() -> List[serial.tools.list_ports.comports]:
    ports = [
        p
        for p in serial.tools.list_ports.comports()
    ]
    if not ports:
        logging.error('%s No Arduino found', log_name)
        raise IOError()
    return ports

def get_arduino_assignments() -> Dict[int, str]:
    assigned_arduinos = []
    for device in _show_all_com_devices():
        if "Arduino" in device.description and device.serial_number in arduino_assignments:
            assigned_arduinos.append((arduino_assignments[device.serial_number], device.device))
    return sorted(assigned_arduinos)

if __name__ == '__main__':
    for i in _show_all_com_devices():
        print(f"{i.description}, {i.device}, {i.serial_number}, {i.name}")

    print()

    print(get_arduino_assignments())

        