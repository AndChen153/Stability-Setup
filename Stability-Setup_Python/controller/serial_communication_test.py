import serial
import time

# Initialize serial connection
ser = serial.Serial('COM3', 115200, timeout=1)  # Replace 'COM3' with your port
time.sleep(2)  # Wait for Arduino to reset

# Function to send parameters
def send_parameters(mode, val1, val2, val3, val4, val5):
    command = f"<{mode},{val1},{val2},{val3},{val4},{val5}>"
    ser.write(command.encode())
    print(f"Sent: {command}")
def read_response():
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"Arduino: {response}")

read_response()
send_parameters("START", 1.0, 2.0, 3, 4, 5)
while True:
    read_response()
