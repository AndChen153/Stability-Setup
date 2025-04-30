import subprocess
import os
import threading
import serial.tools.list_ports
import argparse
import time
import re

# Path to your Arduino/ESP32 sketch
SKETCH_PATH = os.path.join(os.path.dirname(__file__),"Stability-Setup_Arduino.ino")

# List all serial devices
def _show_all_com_devices():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise IOError("No serial devices found.")
    return ports

# Detect Arduino Nano (CH340)
def list_arduino_boards_nano():
    return [(d.device, 'arduino:avr:nano')
            for d in _show_all_com_devices()
            if 'CH340' in d.description.upper()]

# Detect Arduino Uno
def list_arduino_boards_uno():
    return [(d.device, 'arduino:avr:uno')
            for d in _show_all_com_devices()
            if 'UNO' in d.description.upper()]

# Detect Arduino Mega
def list_arduino_boards_mega():
    return [(d.device, 'arduino:avr:mega')
            for d in _show_all_com_devices()
            if 'MEGA' in d.description.upper()]

# Detect ESP32-S3 boards (including Seeed XIAO-ESP32S3)
def list_esp32_s3_boards():
    esp_devices = []
    for d in _show_all_com_devices():
        desc = d.description.upper()
        # Common USB-serial bridges/drivers on ESP32-S3 dev boards
        if any(keyword in desc for keyword in ['CP210', 'USB SERIAL', 'CH910', 'SILABS', 'XIAO', 'ESP32']):
            esp_devices.append((d.device, 'esp32:esp32:esp32s3'))
    return esp_devices

# Compile sketch and report memory usage
def compile_sketch(fqbn: str) -> bool:
    print(f"Compiling sketch for {fqbn}...")
    cmd = ["arduino-cli", "compile", "--fqbn", fqbn, SKETCH_PATH]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        return False

    print("Compilation successful!")
    print(result.stdout)

    return True

# Upload to a single board with verbose logging; set baud to 9600; catch known ESP32 reset errors
def upload_to_board(port: str, fqbn: str):
    # baud = 115200
    # print(f"\nUploading to {port} ({fqbn}) at {baud} baud...")
    cmd = [
        "arduino-cli", "--verbose", "upload",
        "--port", port,
        "--fqbn", fqbn,
        # "--upload-property", f"upload.speed={baud}",
        # "--upload-property", "upload.tool=esptool_py",
        # "--upload-property", "esptool.before=default_reset",
        SKETCH_PATH
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr:
        print("Upload stderr:")
        print(result.stderr)

    stub_errors = [
        "A device which does not exist was specified",
        "Cannot configure port",
        "A serial exception error occurred"
    ]
    if result.returncode != 0 and any(err in result.stderr for err in stub_errors):
        print(f"⚠️  Detected ESP32 stub-reset on {port}, but firmware was written.")
        return

    if result.returncode == 0:
        print(f"✅  Upload successful to {port}")
    else:
        print(f"❌  Upload failed for {port} with exit code {result.returncode}")

# Flash all boards of specified type
def flash_all_boards(board_type: str):
    detectors = {
        'nano': list_arduino_boards_nano,
        'uno':  list_arduino_boards_uno,
        'mega': list_arduino_boards_mega,
        'esp32-s3': list_esp32_s3_boards
    }
    detector = detectors.get(board_type)
    if not detector:
        print(f"Unsupported board type: {board_type}")
        return

    boards = detector()
    if not boards:
        print(f"No {board_type} boards detected!")
        return
    print(f"Detected {len(boards)} {board_type} board(s):")
    for port, fqbn in boards:
        print(f"- {port} ({fqbn})")

    # Compile sketch
    if not compile_sketch(boards[0][1]):
        print("Skipping upload due to compilation failure.")
        return

    # Small delay before upload
    time.sleep(0.5)

    # Parallel uploads
    threads = []
    for port, fqbn in boards:
        t = threading.Thread(target=upload_to_board, args=(port, fqbn))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print("\nFlashing complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compile & flash Arduino Nano, Uno, Mega, or ESP32-S3 boards in parallel."
    )
    parser.add_argument(
        '--board', '-b', choices=['nano', 'uno', 'mega', 'esp32-s3'], default='nano',
        help="Board type: 'nano', 'uno', 'mega', or 'esp32-s3'."
    )
    args = parser.parse_args()
    flash_all_boards(args.board)
