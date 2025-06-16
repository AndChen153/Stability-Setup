# Stability Measurement System

A Python GUI application for managing long-term device stability trials, real-time data collection, Arduino control, and visualization results.

**Installation and Arduino Firmware Flashing steps are required for completely functionality.**

---

## Installation

### 1. Using the Precompiled `.exe` (Recommended for End Users)

- Download the latest `StabilitySetup.exe` from the release folder.
- Double-click to run. No Python or additional installation is required.
- If Windows Defender blocks it, click **"More Info" → "Run anyway"**.

### 2. From Source (for Developers)

#### Requirements:
- Python 3.9–3.11 (miniconda recommended)
- Windows OS (tested on Windows 10/11)
- Arduino devices connected via USB

#### Setup Steps:

```bash
# Clone the repo
git clone https://github.com/your-org/stability-setup.git
cd stability-setup

# Create and activate a Conda environment
conda create -n stabilitySetup python=3.10
conda activate stabilitySetup

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

```

## Arduino Firmware Flashing

### Installing Arduino CLI

The flash script requires Arduino CLI to be installed:

1. Download Arduino CLI from [arduino.cc/cli](https://arduino.cc/cli)
2. Add it to your system PATH
3. Initialize the CLI and install required board packages:

```bash
# Initialize Arduino CLI
arduino-cli config init

# Install required board packages
arduino-cli core install arduino:avr        # For Nano/Uno/Mega
arduino-cli core install esp32:esp32        # For ESP32 boards

# Install required libraries
arduino-cli lib install "Adafruit INA219"
arduino-cli lib install "Adafruit MCP4725"
```

### Using flash.py

The `flash.py` script allows you to easily compile and upload the Arduino firmware to multiple boards simultaneously. It now includes enhanced device detection capabilities to help identify and add support for new board types.

```bash
# Navigate to the Arduino firmware directory
cd Stability-Setup_Arduino

# Flash Arduino Nano boards (default)
python flash.py

# Flash other supported board types
python flash.py --board uno
python flash.py --board mega
python flash.py --board esp32-s3

# Show detailed information about all connected devices
# (useful for identifying new board types)
python flash.py --list-devices
```

### Adding Support for New Board Types

The `flash.py` script includes a helper function to easily identify and add support for new board types.

#### Step 1: Identify Your Board

First, connect your new board and run the device detection command:

```bash
python flash.py --list-devices
```

This will show detailed information about all connected serial devices, including:
- Device path (e.g., COM3, /dev/ttyUSB0)
- Description (most important for identification)
- Manufacturer, Product, Vendor/Product IDs
- Hardware ID and other technical details

If you are unsure about what to look for, try connecting and disconnecting your board to see what changes in the output.

#### Step 2: Add Board Support

Look at the **Description** field to identify unique keywords for your board type, then add support using the helper function inside of `flash.py`:

```python
# Example: Adding support for a new board type
list_my_new_board = create_board_detector(['KEYWORD1', 'KEYWORD2'], 'vendor:arch:board')
```

#### Step 3: Complete the Integration

1. Add your new detector to the `detectors` dictionary in the `flash_all_boards()` function
2. Install the required Arduino core package:
   ```bash
   arduino-cli core install vendor:architecture
   ```
3. Add your board type to the command-line choices in the argument parser

#### Example: Adding ESP32-C3 Support

```python
# 1. Run python flash.py --list-devices and identify keywords like 'ESP32-C3'
# 2. Create detector
list_esp32_c3_boards = create_board_detector(['ESP32-C3', 'CP210'], 'esp32:esp32:esp32c3')

# 3. Add to detectors dictionary
detectors = {
    'nano': list_arduino_boards_nano,
    'uno': list_arduino_boards_uno,
    'mega': list_arduino_boards_mega,
    'esp32-s3': list_esp32_s3_boards,
    'esp32-c3': list_esp32_c3_boards  # Add this line
}

# 4. Install core
# arduino-cli core install esp32:esp32
```

