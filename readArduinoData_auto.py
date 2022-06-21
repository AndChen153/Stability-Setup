#!/usr/bin/env python3
import serial
import time
import csv

filename = "data.csv"
fields = ["Output Volts", "Load Voltage", "Amperage (mA)"]

f = open('data.csv', 'w')
writer = csv.writer(f)
writer.writerow(fields)

def take_input(val):
    # input_value = input('0.000-3.300: ')
    input_value = val
    if (input == "quit"):
        f.close()
        exit()

    input_value = float(input_value)*4096.0/3.3
    input_value = round(input_value)
    return input_value

if __name__ == '__main__':
    ser = serial.Serial('COM4', 115200, timeout=1)
    ser.flush()

    count = -5
    input_value = 0
    voltage_val = 0
    while voltage_val < 1.1:
        if count > 3:
            voltage_val += 0.05
            input_value = take_input(voltage_val)
            # print(voltage_val)
            count = 0
        if ser.in_waiting > 0:
            ser.write(str(input_value).encode())
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            count += 1
            data_list = line.split(",")
            # if (float(data_list[0]) > 0.1):
            #     print (data_list)
            #     writer.writerow(data_list)
            #     count += 1
