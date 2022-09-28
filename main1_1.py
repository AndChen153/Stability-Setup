#!/usr/bin/env python3
import serial
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
start = time.time()

# params that have worked in the past
# SCAN_RANGE = 1.2
# SCAN_STEP_SIZE = 0.03
# SCAN_READ_COUNT = 3
# SCAN_RATE = 100         # mV/s

# PNO_STARTING_VOLTAGE = 0.9
# PNO_STEP_SIZE = 0.02
# PNO_MEASUREMENTS_PER_STEP = 5
# PNO_MEASUREMENT_DELAY = 100


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



class StabilitySetup:

    def __init__(self, COM: str, SERIAL_BAUD_RATE: int) -> None:
        """
        Parameters
        ----------
        COM : str
            com port to communicate with arduino
            typically "COM5" or "COM3"
        SERIAL_BAUD_RATE : str
            serial rate to communicate with arduino
            set to 115200 in arduino code
        """
        self.ser = serial.Serial(COM, SERIAL_BAUD_RATE, timeout=1)
        self.ser.flush()

    def readData(self):
        """
        Reads data outputed on serial bus by arduino
        """
        done = False
        line = ""
        while not done:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                data_list = line.split(",")
                # print(data_list)

                print(line)

                if len(data_list) > 10:
                    self.arr = np.append(self.arr, np.array([data_list]),axis = 0)

                if line == "Done!":
                    done = True


    def saveData(self):
        """
        saves numpy array to csv file
        """
        np.savetxt(fileName, self.arr, delimiter=",", fmt='%s')


    def printTime(self):
        end = time.time()
        total_time = end - start
        print("\n"+ str(total_time))


    def Scan(self, SCAN_RANGE: float, SCAN_STEP_SIZE: float, SCAN_READ_COUNT: int, SCAN_RATE: int, SCAN_MODE: int) -> np.ndarray:
        """
        Parameters
        ----------
        SCAN_RANGE : float
            voltage range in which scan will run, starts from 0
            1.2 V
        SCAN_STEP_SIZE : float
            step size that voltage will increase and decrease by during the scan
            0.03 V
        SCAN_READ_COUNT : int
            how many times per voltage step the setup takes a voltage reading
            3
        SCAN_RATE : int
            rate at which scan will progress
            100 mV/s
        SCAN_MODE : int
            scan in the light or in the dark
            0 = dark, 1 = light

        Returns
        -------
        arr
            numpy array setup for a scan
        """
        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")

        self.fileName = "./data/scan" + scanMode + today + ".csv"

        self.parameters = "<scan," + str(SCAN_RANGE) + "," + str(SCAN_STEP_SIZE) + "," + str(SCAN_READ_COUNT) + "," + str(SCAN_RATE) + ">"

        self.arr = np.empty([5, 18], dtype="object")
        self.arr[0][0] = "Voltage Range: " + str(SCAN_RANGE)
        self.arr[1][0] = "Voltage Step Size: " + str(SCAN_STEP_SIZE)
        self.arr[2][0] = "Voltage Read Count: " + str(SCAN_READ_COUNT)
        self.arr[3][0] = "Voltage Delay Time: " + str(SCAN_RATE)
        self.arr[4] = ["Volts_output", "Pixel 0 V", "Pixel 0 mA","Pixel 1 V", "Pixel 1 mA","Pixel 2 V", "Pixel 2 mA","Pixel 3 V", "Pixel 3 mA","Pixel 4 V", "Pixel 4 mA","Pixel 5 V", "Pixel 5 mA","Pixel 6 V", "Pixel 6 mA","Pixel 7 V", "Pixel 7 mA", "Time"]

        self.readData()
        print(self.arr)
        self.printTime
        return self.arr


    def PnO(self, PNO_STARTING_VOLTAGE: float, PNO_STEP_SIZE: float, PNO_MEASUREMENTS_PER_STEP: int, PNO_MEASUREMENT_DELAY: int) -> np.ndarray:
        """
        Parameters
        ----------
        PNO_STARTING_VOLTAGE : float
            voltage point where the measurement will start
            0.09 V
        PNO_STEP_SIZE : float
            step size that voltage will increase and decrease by during the measurement
            0.02 V
        PNO_MEASUREMENTS_PER_STEP : int
            how many times per voltage step the setup takes a voltage reading
            5
        PNO_MEASUREMENT_DELAY : int
            rate at which pno alg will progress
            100 mV/s

        Returns
        -------
        arr
            numpy array filled with data
        """

        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.fileName = "./data/PnO" + today + ".csv"

        self.parameters = "<PnO," + str(PNO_STARTING_VOLTAGE) + "," + str(PNO_STEP_SIZE) + "," + str(PNO_MEASUREMENTS_PER_STEP) + "," + str(PNO_MEASUREMENT_DELAY) + ">"

        self.arr = np.empty([5, 26], dtype="object")
        self.arr[0][0] = "Voltage Range: " + str(PNO_STARTING_VOLTAGE)
        self.arr[1][0] = "Voltage Step Size: " + str(PNO_STEP_SIZE)
        self.arr[2][0] = "Voltage Read Count: " + str(PNO_MEASUREMENTS_PER_STEP)
        self.arr[3][0] = "Voltage Delay Time: " + str(PNO_MEASUREMENT_DELAY)
        self.arr[4] = ["Time","Pixel 0 V","Pixel 0 mA","Pixel 1 V","Pixel 1 mA","Pixel 2 V","Pixel 2 mA","Pixel 3 V","Pixel 3 mA","Pixel 4 V","Pixel 4 mA","Pixel 5 V","Pixel 5 mA","Pixel 6 V","Pixel 6 mA","Pixel 7 V","Pixel 7 mA", "Pixel 0 PCE", "Pixel 1 PCE", "Pixel 2 PCE", "Pixel 3 PCE", "Pixel 4 PCE", "Pixel 5 PCE", "Pixel 6 PCE", "Pixel 7 PCE", "Filler Val"]

        self.readData()
        print(self.arr)
        self.printTime

        return self.arr





line = ""
run = True
done = False

# print(arr)
if __name__ == '__main__':
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

