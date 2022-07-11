#!/usr/bin/env python3
import serial
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

start = time.time()

VOLTAGE_RANGE = 1.2
VOLTAGE_STEP_SIZE = 0.01
VOLTAGE_READ_COUNT = 10
VOLTAGE_DELAY_TIME = 5         # 1/10 of 50

VOLTAGE_Starting_PNO = 0.4
VOLTAGE_STEP_SIZE_PNO = 0.09
VOLTAGE_READ_COUNT_PNO = 5
VOLTAGE_DELAY_TIME_PNO = 25


COM = 'COM3'
SERIAL_BAUD_RATE = 115200

mode = "PnO"
message = ""
arr = np.array([])

if (mode == "scan"):
    message = "<scan," + str(VOLTAGE_RANGE) + "," + str(VOLTAGE_STEP_SIZE) + "," + str(VOLTAGE_READ_COUNT) + "," + str(VOLTAGE_DELAY_TIME) + ">"
    arr = np.array([["Voltage Range: " + str(VOLTAGE_RANGE),           " ", " ", " "],
                    ["Voltage Step Size: " + str(VOLTAGE_STEP_SIZE),   " ", " ", " "],
                    ["Voltage Read Count: " + str(VOLTAGE_READ_COUNT), " ", " ", " "],
                    ["Voltage Delay Time: " + str(VOLTAGE_DELAY_TIME), " ", " ", " "],
                    ["Volts_output", "Pixel 1 V", "Pixel 1 mA", "Time"]])
elif (mode == "PnO"):
    message = "<PnO," + str(VOLTAGE_Starting_PNO) + "," + str(VOLTAGE_STEP_SIZE_PNO) + "," + str(VOLTAGE_READ_COUNT_PNO) + "," + str(VOLTAGE_DELAY_TIME_PNO) + ">"
    arr = np.array([["Voltage Range: " + str(VOLTAGE_Starting_PNO),            " ", " ", " ", " "],
                    ["Voltage Step Size: " + str(VOLTAGE_STEP_SIZE_PNO),       " ", " ", " ", " "],
                    ["Measurement Read Count: " + str(VOLTAGE_READ_COUNT_PNO), " ", " ", " ", " "],
                    ["Measurement Delay Time: " + str(VOLTAGE_DELAY_TIME_PNO), " ", " ", " ", " "],
                    ["Volts_output","Pixel 1 V","Pixel 1 mA", "Pixel 1 PCE", "Time"]])


today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")

line = ""
run = True


if __name__ == '__main__':
    ser = serial.Serial(COM, SERIAL_BAUD_RATE, timeout=1)
    ser.flush()

    while line != "Done!":
        if ser.in_waiting > 0:
            if run:
                ser.write(message.encode())
                print(today)
                run = False

            line = ser.readline().decode('utf-8').rstrip()
            data_list = line.split(",")
            # print(data_list)
            print(line)
            if len(data_list) > 2:
            #     print(line)
            #     # print(np.array([data_list]))
            #     # print(np.array([data_list]).shape)
                arr = np.append(arr, np.array([data_list]),axis = 0)

    print ("\n")
    print(arr)
    np.savetxt("./data/" + mode + "_" + today + ".csv", arr, delimiter=",", fmt='%s')
    # pltarr = np.delete(arr, [0,1,2,3], axis=0)


    # plt.plot(pltarr[ :,1],pltarr[ :,2])
    # plt.title(message)
    # plt.xlabel('Voltage')
    # plt.ylabel('Current')
    # plt.show()


    end = time.time()
    total_time = end - start
    print("\n"+ str(total_time))
