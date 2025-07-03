import serial.tools.list_ports
from typing import Dict, List

from helper.global_helpers import get_logger


def _show_all_com_devices() -> List[serial.Tools.ListPorts.comports]:
    ports = [p for p in serial.tools.list_ports.comports()]
    if not ports:
        get_logger().error("No Arduino found")
        raise IOError("No Arduino found")
    return ports


def get() -> List[str]:
    """Get a list of connected Arduino devices."""
    try:
        return [
            device.device
            for device in _show_all_com_devices()
            if any(
                substr in device.description
                for substr in ["USB Serial Device", "USB-SERIAL CH340", "Arduino Mega 2560"]
            )
        ]
    except IOError:
        return []


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

