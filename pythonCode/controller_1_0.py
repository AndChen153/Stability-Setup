#!/usr/bin/env python3
import serial
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
start = time.time()

VOLTAGE_RANGE = 1.2
VOLTAGE_STEP_SIZE = 0.03
VOLTAGE_READ_COUNT = 3
VOLTAGE_SCAN_RATE = 100         # mV/s

VOLTAGE_Starting_PNO = 0.9
VOLTAGE_STEP_SIZE_PNO = 0.02
MEASUREMENTS_PER_STEP_PnO = 5
MEASUREMENT_DELAY_PnO = 100

COM = 'COM5'
SERIAL_BAUD_RATE = 115200

modeInput = int(input("0 for scan, 1 for pno"))
if modeInput == 0:
    mode = "scan"
    scanModeInput = int(input("0 for dark, 1 for light"))
    if scanModeInput == 0:
        scanMode = "dark_"
    else:
        scanMode = "light_"
    fileName = "./data/" + mode + scanMode + today + ".csv"
else:
    mode = "PnO"
    fileName = "./data/" + mode + today + ".csv"


scanMessage = "<scan," + str(VOLTAGE_RANGE) + "," + str(VOLTAGE_STEP_SIZE) + "," + str(VOLTAGE_READ_COUNT) + "," + str(VOLTAGE_SCAN_RATE) + ">"
pnoMessage = "<PnO," + str(VOLTAGE_Starting_PNO) + "," + str(VOLTAGE_STEP_SIZE_PNO) + "," + str(MEASUREMENTS_PER_STEP_PnO) + "," + str(MEASUREMENT_DELAY_PnO) + ">"

def resetScanArr():
    global arr
    arr = np.empty([5, 18], dtype="object")
    arr[0][0] = "Voltage Range: " + str(VOLTAGE_RANGE)
    arr[1][0] = "Voltage Step Size: " + str(VOLTAGE_STEP_SIZE)
    arr[2][0] = "Voltage Read Count: " + str(VOLTAGE_READ_COUNT)
    arr[3][0] = "Voltage Delay Time: " + str(VOLTAGE_SCAN_RATE)
    arr[4] = ["Volts_output", "Pixel 0 V", "Pixel 0 mA","Pixel 1 V", "Pixel 1 mA","Pixel 2 V", "Pixel 2 mA","Pixel 3 V", "Pixel 3 mA","Pixel 4 V", "Pixel 4 mA","Pixel 5 V", "Pixel 5 mA","Pixel 6 V", "Pixel 6 mA","Pixel 7 V", "Pixel 7 mA", "Time"]

def resetPnO():
    global arr
    arr = np.empty([5, 26], dtype="object")
    arr[0][0] = "Voltage Range: " + str(VOLTAGE_Starting_PNO)
    arr[1][0] = "Voltage Step Size: " + str(VOLTAGE_STEP_SIZE_PNO)
    arr[2][0] = "Voltage Read Count: " + str(MEASUREMENTS_PER_STEP_PnO)
    arr[3][0] = "Voltage Delay Time: " + str(MEASUREMENT_DELAY_PnO)
    arr[4] = ["Time","Pixel 0 V","Pixel 0 mA","Pixel 1 V","Pixel 1 mA","Pixel 2 V","Pixel 2 mA","Pixel 3 V","Pixel 3 mA","Pixel 4 V","Pixel 4 mA","Pixel 5 V","Pixel 5 mA","Pixel 6 V","Pixel 6 mA","Pixel 7 V","Pixel 7 mA", "Pixel 0 PCE", "Pixel 1 PCE", "Pixel 2 PCE", "Pixel 3 PCE", "Pixel 4 PCE", "Pixel 5 PCE", "Pixel 6 PCE", "Pixel 7 PCE", "Filler Val"]

# arr = np.array([["Voltage Range: " + str(VOLTAGE_Starting_PNO),            " ", " ", " ", " "],
#                 ["Voltage Step Size: " + str(VOLTAGE_STEP_SIZE_PNO),       " ", " ", " ", " "],
#                 ["Measurement Read Count: " + str(MEASUREMENTS_PER_STEP_PnO), " ", " ", " ", " "],
#                 ["Measurement Delay Time: " + str(MEASUREMENT_DELAY_PnO), " ", " ", " ", " "],
#                 ["Pixel VSet","Pixel  V","Pixel  mA", "Pixel  PCE", "Time"]])



line = ""
run = True
done = False

# print(arr)
if __name__ == '__main__':
    ser = serial.Serial(COM, SERIAL_BAUD_RATE, timeout=1)
    ser.flush()
    # while line != "Done!":
    while not done:

        if ser.in_waiting > 0:
            if run:
                if mode == "scan":
                    resetScanArr()
                    ser.write(scanMessage.encode())
                elif mode == "PnO":
                    resetPnO()
                    ser.write(pnoMessage.encode())
                run = False

            line = ser.readline().decode('utf-8').rstrip()
            data_list = line.split(",")
            # print(data_list)

            print(line)

            if len(data_list) > 10:
                arr = np.append(arr, np.array([data_list]),axis = 0)
            #     # print(np.array([data_list]))
                # print(np.array([arr]).shape)


            if line == "Done!":
                # run = True
                done = True
                # UNCOMMENT THIS LINE TO SAVE
                np.savetxt(fileName, arr, delimiter=",", fmt='%s')

            #     if mode == "PnO":
            #         done = True
            #         run = False
            #     mode = "PnO"

            ####add functionality to send 0.8*VoC to Arduino for VSet



    print ("\n")
    print(arr)
    print(fileName)
    # pltarr = np.delete(arr, [0,1,2,3], axis=0)


    # plt.plot(pltarr[ :,1],pltarr[ :,2])
    # plt.title(message)
    # plt.xlabel('Voltage')
    # plt.ylabel('Current')
    # plt.show()


    end = time.time()
    total_time = end - start
    print("\n"+ str(total_time))

