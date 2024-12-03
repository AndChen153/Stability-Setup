#!/usr/bin/env python3
from numpy import double, void
import serial
import time
import csv
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

start = time.time()



VOLTAGE_RANGE = 1.2
VOLTAGE_STEP_SIZE = 0.05    # make sure to change this in arduino program as well
VOLTAGE_READ_COUNT = 3
COM = 'COM3'
SERIAL_BAUD_RATE = 115200


filename = "data.csv"
fields = ["Output Volts", "Load Voltage", "Amperage (mA)"]

f = open('data.csv', 'w')
writer = csv.writer(f)
writer.writerow(fields)


def convert_to_12bit(val: float):
    # calculate 12 bit value for voltage in range of 0-3.3 volts

    if (val == "quit"):
        f.close()
        exit()
    elif (val < 0 or val > 3.3):
        return 0

    val = float(val)*4095.0/3.3
    val = round(val)
    return val


def scan(volt_Range: float, volt_Step_Size: float, volt_Read_Count: int, direction: str) -> void:
    count = 1              # gives time for voltage readings to reset to 0
    input_value = 0
    voltage_val = 0

    avgVolt = 0
    avgCurr = 0


    if (direction == "foward" or direction == "both"):
        while voltage_val < volt_Range:


            if count > volt_Read_Count:                         # run each voltage step for 3 readings
                voltage_val += volt_Step_Size
                input_value = convert_to_12bit(voltage_val)
                # send new voltage value to arduino
                ser.write(str(input_value).encode())
                print(str(round(avgVolt/3.0, 3)) + "," + str(round(avgCurr/3.0),3))
                avgVolt = 0
                avgCurr = 0
                count = 1

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()  # read current data from arduino
                # print(line)
                data_list = line.split(",")
                # avgVolt += float(data_list[1])
                # avgCurr += float(data_list[2])

                if (float(data_list[0]) > 0.1):
                    print (line)
                #     writer.writerow(data_list)
                #     count += 1

                count += 1


    voltage_val = volt_Range + volt_Step_Size
    if (direction == "backward" or direction == "both"):
        while voltage_val > 0:
            if count > volt_Read_Count:                         # run each voltage step for 3 readings
                voltage_val -= volt_Step_Size
                input_value = convert_to_12bit(voltage_val)
                # send new voltage value to arduino
                ser.write(str(input_value).encode())
                print(str(round(avgVolt/3.0, 3)) + "," + str(round(avgCurr/3.0,3)))
                avgVolt = 0
                avgCurr = 0
                count = 1

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()  # read current data from arduino
                # print(line)
                data_list = line.split(",")
                # avgVolt += float(data_list[1])
                # avgCurr += float(data_list[2])

                if (float(data_list[0]) > 0.1):
                    print(line)
                #     print (data_list)
                #     writer.writerow(data_list)
                #     count += 1

                count += 1


if __name__ == '__main__':
    ser = serial.Serial(COM, SERIAL_BAUD_RATE, timeout=1)
    ser.flush()
    print("started");

    # message = "<Stability_Setup," + str(VOLTAGE_RANGE) + "," + str(VOLTAGE_STEP_SIZE) + "," + str(VOLTAGE_READ_COUNT) + ">"
    # while True:
    #     ser.write(message.encode())
    #     if ser.in_waiting > 0:
    #         line = ser.readline().decode('utf-8').rstrip()
    #         print(line)

    # run backwards first
    scan(VOLTAGE_RANGE, VOLTAGE_STEP_SIZE, VOLTAGE_READ_COUNT, "backward")
    scan(VOLTAGE_RANGE, VOLTAGE_STEP_SIZE, VOLTAGE_READ_COUNT, "forward")
    end = time.time()
    total_time = end - start
    print("\n"+ str(total_time))