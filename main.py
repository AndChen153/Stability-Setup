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
COM = 'COM3'
SERIAL_BAUD_RATE = 115200

message = "<Stability_Setup," + str(VOLTAGE_RANGE) + "," + str(VOLTAGE_STEP_SIZE) + "," + str(VOLTAGE_READ_COUNT) + ">"

today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
arr = np.array([["Voltage Range: " + str(VOLTAGE_RANGE), " ", " "],
                ["Voltage Step Size: " + str(VOLTAGE_STEP_SIZE), " ", " "],
                ["Voltage Read Count: " + str(VOLTAGE_READ_COUNT), " ", " "],
                ["Volts_output","Volts Pixel 1", "Current Pixel 1"]])

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
            if len(data_list) > 2:
                print(np.array([data_list]))
                # print(np.array([data_list]).shape)
                arr = np.append(arr, np.array([data_list]),axis = 0)

    # print("\n")
    # print (arr)
    np.savetxt("./data/" + today + ".csv", arr, delimiter=",", fmt='%s')
    pltarr = np.delete(arr, [0,1,2,3], axis=0)


    plt.plot(pltarr[ :,1],pltarr[ :,2])
    plt.title(message)
    plt.xlabel('Voltage')
    plt.ylabel('Current')
    # plt.show()


    end = time.time()
    total_time = end - start
    print("\n"+ str(total_time))
