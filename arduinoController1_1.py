#!/usr/bin/env python3
from email import header
from fileinput import filename
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

    # def __init__(self) -> None:
    #     pass

    def _readData(self):
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


    def saveData(self) -> str:
        """
        saves numpy array to csv file

        Returns
        -------
        fileName
            fileName for file that was just saved
        """
        np.savetxt(self.fileName, self.arr, delimiter=",", fmt='%s')
        return self.fileName


    def printTime(self):
        end = time.time()
        total_time = end - start
        print("\n"+ str(total_time))


    def scan(self, SCAN_RANGE: float, SCAN_STEP_SIZE: float, SCAN_READ_COUNT: int, SCAN_RATE: int, LIGHT_STATUS: int) -> np.ndarray:
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
            3ser.
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
        filename
            name of file that data will be saved to
        """
        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")

        if LIGHT_STATUS == 0:
            light = "dark"
        else:
            light = "light"

        self.fileName = "./data/scan" + light + today + ".csv"

        self.parameters = "<scan," + str(SCAN_RANGE) + "," + str(SCAN_STEP_SIZE) + "," + str(SCAN_READ_COUNT) + "," + str(SCAN_RATE) + "," + str(LIGHT_STATUS) + ">"


        headerArr = ["Volts_output",
                       "Pixel 0 V", "Pixel 0 mA",
                       "Pixel 1 V", "Pixel 1 mA",
                       "Pixel 2 V", "Pixel 2 mA",
                       "Pixel 3 V", "Pixel 3 mA",
                       "Pixel 4 V", "Pixel 4 mA",
                       "Pixel 5 V", "Pixel 5 mA",
                       "Pixel 6 V", "Pixel 6 mA",
                       "Pixel 7 V", "Pixel 7 mA",
                       "Time"]

        self.arr = np.empty([6, len(headerArr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", SCAN_RANGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", SCAN_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: " , SCAN_READ_COUNT
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", SCAN_RATE
        self.arr[4][0], self.arr[4][1] = "Light Status: ",  light
        self.arr[5] = headerArr

        self.ser.write(self.parameters.encode())  # send data to arduino
        self._readData()
        print(self.arr)
        self.printTime()
        self.saveData()
        return self.arr, self.fileName


    def pno(self, PNO_STARTING_VOLTAGE: float, PNO_STEP_SIZE: float, PNO_MEASUREMENTS_PER_STEP: int, PNO_MEASUREMENT_DELAY: int, DUMMY: int) -> np.ndarray:
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
        filename
            name of file that data will be saved to
        """

        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.fileName = "./data/PnO" + today + ".csv"

        self.parameters = "<PnO," + str(PNO_STARTING_VOLTAGE) + "," + str(PNO_STEP_SIZE) + "," + str(PNO_MEASUREMENTS_PER_STEP) + "," + str(PNO_MEASUREMENT_DELAY) + "," + str(DUMMY) + ">"

        headerArr  = ["Time",
                       "Pixel 0 V","Pixel 0 mA",
                       "Pixel 1 V","Pixel 1 mA",
                       "Pixel 2 V","Pixel 2 mA",
                       "Pixel 3 V","Pixel 3 mA",
                       "Pixel 4 V","Pixel 4 mA",
                       "Pixel 5 V","Pixel 5 mA",
                       "Pixel 6 V","Pixel 6 mA",
                       "Pixel 7 V","Pixel 7 mA",
                       "Pixel 0 PCE", "Pixel 1 PCE",
                       "Pixel 2 PCE", "Pixel 3 PCE",
                       "Pixel 4 PCE", "Pixel 5 PCE",
                       "Pixel 6 PCE", "Pixel 7 PCE",
                       "Filler Val"]

        self.arr = np.empty([5, len(headerArr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", PNO_STARTING_VOLTAGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", PNO_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: ", PNO_MEASUREMENTS_PER_STEP
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", PNO_MEASUREMENT_DELAY
        self.arr[4] = headerArr

        self.ser.write(self.parameters.encode())  # send data to arduino
        self._readData()
        print(self.arr)
        self.printTime()
        self.saveData()

        return self.arr, self.fileName