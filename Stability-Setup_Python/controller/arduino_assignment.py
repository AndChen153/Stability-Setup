import serial.tools.list_ports
import logging
from typing import Dict, List
log_name = 'arduino_assignment'

def _show_all_com_devices() -> List[serial.tools.list_ports.comports]:
    ports = [
        p
        for p in serial.tools.list_ports.comports()
    ]
    if not ports:
        logging.error('%s No Arduino found', log_name)
        raise IOError()
    return ports

def get():
    connected_arduinos = []
    for device in _show_all_com_devices():
        if any(substr in device.description for substr in ["USB Serial Device", "USB-SERIAL CH340", "Arduino Mega 2560"]):
            connected_arduinos.append(device.device)

    return connected_arduinos

if __name__ == '__main__':
    # get_logger().log(_show_all_com_devices())

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


    print(get())

