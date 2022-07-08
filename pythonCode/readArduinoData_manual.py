#!/usr/bin/env python3
import serial
import time
import csv

filename = "data.csv"
fields = ["Output Volts", "Load Voltage", "Amperage (mA)"]

f = open('data.csv', 'w')
writer = csv.writer(f)
writer.writerow(fields)

def take_input():
    input_value = input('0.000-3.300: ')
    if (input == "quit"):
        f.close()
        exit()

    input_value = float(input_value)*4095.0/3.3
    input_value = round(input_value)
    return input_value

if __name__ == '__main__':
    ser = serial.Serial('COM3', 115200, timeout=1)
    ser.flush()

    count = 16
    input_value = 0
    while True:
        if count > 15:
            ser.write(str(0).encode())
            input_value = take_input()
            count = 0
        if ser.in_waiting > 0:
            ser.write(str(input_value).encode())
            line = ser.readline().decode('utf-8').rstrip()
            print (line)
            data_list = line.split(",")
            if (float(data_list[0]) > 0.1):

                writer.writerow(data_list)
                count += 1
