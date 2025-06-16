import subprocess
import os
import threading
import serial.tools.list_ports
import argparse
import time

# Path to your Arduino/ESP32 sketch
SKETCH_PATH = os.path.join(os.path.dirname(__file__),"Stability-Setup_Arduino.ino")

# List all serial devices
def _show_all_com_devices():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise IOError("No serial devices found.")
    return ports

# Show detailed information about all COM devices for identifying new board types
def show_device_details():
    """
    Display detailed information about all connected serial devices.
    This is useful for identifying new board types and their characteristics.
    """
    try:
        devices = _show_all_com_devices()
        print(f"\nFound {len(devices)} serial device(s):")
        print("=" * 80)

        for i, device in enumerate(devices, 1):
            print(f"\nDevice {i}:")
            print(f"  Device: {device.device}")
            print(f"  Name: {device.name}")
            print(f"  Description: {device.description}")
            print(f"  Serial Number: {device.serial_number}")
            print(f"  Manufacturer: {device.manufacturer}")
            print(f"  Product: {device.product}")
            print(f"  Vendor ID: {device.vid}")
            print(f"  Product ID: {device.pid}")
            print(f"  Location: {device.location}")
            print(f"  Hardware ID: {device.hwid}")
            print(f"  Interface: {device.interface}")
            print("-" * 40)

        print("\nTo add support for a new board type:")
        print("1. Look at the 'Description' field to identify unique keywords")
        print("2. Create a new detection function using those keywords")
        print("3. Add the function to the detectors dictionary in flash_all_boards()")
        print("4. Install the required Arduino core with 'arduino-cli core install vendor:architecture'")

    except IOError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Helper function to create board detection functions
def create_board_detector(keywords, fqbn):
    """
    Create a board detection function based on description keywords.

    Args:
        keywords: List of keywords to search for in device descriptions (case-insensitive)
        fqbn: Fully Qualified Board Name for arduino-cli (e.g., 'arduino:avr:nano')

    Returns:
        Function that returns list of (device, fqbn) tuples for matching boards

    Example:
        detect_my_board = create_board_detector(['MY_BOARD', 'CUSTOM'], 'arduino:avr:nano')
        boards = detect_my_board()
    """
    def detector():
        return [(d.device, fqbn)
                for d in _show_all_com_devices()
                if any(keyword.upper() in d.description.upper() for keyword in keywords)]
    return detector

# Detect Arduino Nano (CH340) - using helper function
list_arduino_boards_nano = create_board_detector(['CH340'], 'arduino:avr:nano')

# Detect Arduino Uno - using helper function
list_arduino_boards_uno = create_board_detector(['UNO'], 'arduino:avr:uno')

# Detect Arduino Mega - using helper function
list_arduino_boards_mega = create_board_detector(['MEGA'], 'arduino:avr:mega')

# Detect ESP32-S3 boards (including Seeed XIAO-ESP32S3) - using helper function
list_esp32_s3_boards = create_board_detector(
    ['CP210', 'USB SERIAL', 'CH910', 'SILABS', 'XIAO', 'ESP32'],
    'esp32:esp32:esp32s3'
)

# ============================================================================
# TO ADD SUPPORT FOR NEW BOARD TYPES:
# 1. Run: python flash.py --list-devices
# 2. Connect your new board and identify unique keywords in the Description field
# 3. Create a new detector using the helper function:
#    list_my_new_board = create_board_detector(['KEYWORD1', 'KEYWORD2'], 'vendor:arch:board')
# 4. Add your detector to the 'detectors' dictionary in flash_all_boards()
# 5. Install the required core: arduino-cli core install vendor:arch
# ============================================================================

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
        description="Compile & flash Arduino Nano, Uno, Mega, or ESP32-S3 boards in parallel. Use --list-devices to identify new board types."
    )
    parser.add_argument(
        '--board', '-b', choices=['nano', 'uno', 'mega', 'esp32-s3'], default='nano',
        help="Board type: 'nano', 'uno', 'mega', or 'esp32-s3'."
    )
    parser.add_argument(
        '--list-devices', '-l', action='store_true',
        help="Show detailed information about all connected serial devices to help identify new board types."
    )
    args = parser.parse_args()

    if args.list_devices:
        show_device_details()
    else:
        flash_all_boards(args.board)
