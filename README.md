# Stability Measurement System (SMS)

A Python GUI application for managing long-term device stability trials, real-time data collection, Arduino control, and visualization results.

**Installation and Arduino Firmware Flashing steps are required for completely functionality.**

## Hardware

The system is composed of custom-designed hardware to ensure reliable and repeatable measurements. All design files are open-source and available at the links below.

- **SMS Main PCB**: The main controller board that interfaces with the computer and manages the measurement channels. It houses the Arduino, multiplexers, and other core electronic components.
  - [View Main PCB Design Files](httpss://oshwlab.com/achen1192/stability_setup_1_1)
- **Holder PCB**: A small, interchangeable board designed to hold the perovskite solar cell (PSC) devices under test. It connects to the main PCB and ensures a consistent connection to the device.
  - [View Holder PCB Design Files](https://oshwlab.com/achen1192/stability_setup_1_1)
- **3D-Printed Enclosure**: A custom enclosure to house the main PCB and provide mounting points for the holder PCB and other components.
  - [View 3D-Enclosure CAD Model](https://cad.onshape.com/documents/2ae80eb71ffa9f4089d254fa/w/bd8477a473605951929b0fd2/e/aee47ea40cd595c8c4f856f5?renderMode=0&uiState=67abd8afd3a4a8741c8eb95c)
 

## Installation

This project uses **Conda** to manage dependencies. Ensure you have [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

*Note that this app has only been tested on Windows environments and certain libraries used are not available in other OS.

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
conda env create -f environment.yml
conda activate stabilitySetup

# Run the app
python app.py

```

## Arduino Firmware Flashing


### Option 1: Using Arduino IDE (Recommended for single boards)
1.  Download and install the [Arduino IDE](https://www.arduino.cc/en/software).
2.  Open `Stability-Setup_Arduino/Stability-Setup_Arduino.ino`.
3.  **Install Required Libraries:**
    Go to `Sketch` -> `Include Library` -> `Manage Libraries...` and install:
    * `Adafruit INA219`
    * `Adafruit MCP4725`
4.  **Board Settings:**
    * **Board:** Arduino Nano
    * **Processor:** ATmega328P (Try "ATmega328P (Old Bootloader)" if the standard one fails, as this is common for clones).
5.  Select the correct **Port** and click **Upload**.

### Option 2: Using the Automation Script (For bulk flashing)

#### Installing Arduino CLI

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

#### Using flash.py

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


## Usage

### Running the Controller Software
1.  Ensure your Python environment is active:
    ```bash
    conda activate stabilitySetup
    ```
2.  Navigate to the Python source directory:
    ```bash
    cd Stability-Setup_Python
    ```
3.  Run the application:
    ```bash
    python app.py
    ```

