import subprocess
import json
import os
import sys
import threading

# Path to your Arduino sketch
SKETCH_PATH = r"C:\Users\achen\Dropbox\code\Stability-Setup\Stability-Setup_Arduino\Stability-Setup_Arduino.ino"  # Change this!

# Detect connected Arduino boards
def list_arduino_boards():
    try:
        result = subprocess.run(["arduino-cli", "board", "list", "--format", "json"],
                                capture_output=True, text=True, check=True)
        boards = json.loads(result.stdout.strip())
        detected_boards = []
        for board in boards["detected_ports"]:
            port = board["port"]['address']
            fqbn = 'arduino:avr:nano'
            detected_boards.append((port, fqbn))
        return detected_boards
    except Exception as e:
        print(f"Error detecting Arduino boards: {e}")
        return []

# Compile the sketch
def compile_sketch(fqbn):
    try:
        print(f"Compiling sketch for {fqbn}...")
        compile_command = ["arduino-cli", "compile", "--fqbn", fqbn, SKETCH_PATH]
        result = subprocess.run(compile_command, capture_output=True, text=True)
        if result.returncode == 0:
            print("Compilation successful!")
            return True
        else:
            print("Compilation failed:", result.stderr)
            return False
    except Exception as e:
        print(f"Error compiling sketch: {e}")
        return False

# Upload the compiled sketch to a board
def upload_to_board(port, fqbn):
    try:
        print(f"Uploading to {port} ({fqbn})...")
        upload_command = ["arduino-cli", "upload", "-p", port, "--fqbn", fqbn, SKETCH_PATH]
        result = subprocess.run(upload_command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Upload successful to {port}")
        else:
            print(f"Upload failed for {port}: {result.stderr}")
    except Exception as e:
        print(f"Error uploading to {port}: {e}")

# Flash all detected boards in parallel
def flash_all_boards():
    boards = list_arduino_boards()
    if not boards:
        print("No Arduino boards detected!")
        return

    print(f"Detected {len(boards)} Arduino boards:")
    for port, fqbn in boards:
        print(f"- {port} ({fqbn})")

    # Compile the sketch for the first detected board type (assumes all are the same)
    if not compile_sketch(boards[0][1]):
        print("Skipping upload due to compilation failure.")
        return

    # Upload to all boards in parallel
    threads = []
    for port, fqbn in boards:
        t = threading.Thread(target=upload_to_board, args=(port, fqbn))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Flashing complete!")

if __name__ == "__main__":
    # print(list_arduino_boards())
    flash_all_boards()
