#!/usr/bin/env python3
import serial
import time

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.flush()
    while True:
        x = input('0-4096')
        if ser.in_waiting > 0:
            ser.write(x)
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
