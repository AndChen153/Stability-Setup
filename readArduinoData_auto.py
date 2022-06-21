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
    # calculate 12 bit value for voltage in range of 0-3.3 volts

    if (val == "quit"):
        f.close()
        exit()
    elif (val < 0 or val > 3.3):
        return 0

    val = float(val)*4096.0/3.3
    val = round(val)
    return val

if __name__ == '__main__':
    ser = serial.Serial('COM4', 115200, timeout=1)
    ser.flush()

    count = -3                                              # gives time for voltage readings to reset to 0
    input_value = 0
    voltage_val = 0
    while voltage_val < 1.1:
        if count > 3:                                       # run each voltage step for 3 readings
            voltage_val += 0.05
            input_value = take_input(voltage_val)
            # print(voltage_val)
            count = 0
        if ser.in_waiting > 0:
            ser.write(str(input_value).encode())            # send new voltage value to arduino
            line = ser.readline().decode('utf-8').rstrip()  # read current data from arduino
            print(line)
            count += 1
            data_list = line.split(",")
            # if (float(data_list[0]) > 0.1):
            #     print (data_list)
            #     writer.writerow(data_list)
            #     count += 1
