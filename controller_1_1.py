#!/usr/bin/env python3
from email import header
from fileinput import filename
import serial
import time
from datetime import datetime
import time
import numpy as np
import os
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

    # def __init__(self) -> None:
    #     pass

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
        self.mode = ""

    def readData(self):
        """
        * Reads data outputed on serial bus by arduino
        * Saves data after certain interval of time
        * Does not need to manage mode because that is taken care of on the arduino
        """
        done = False
        line = ""
        timeOrig = time.time()
        timeSave = 0.5 # time between saves in minutes
        while not done:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('unicode_escape').rstrip()
                data_list = line.split(",")
                # print(data_list)

                print(line)

                if len(data_list) > 10:
                    self.arr = np.append(self.arr, np.array([data_list]),axis = 0)

                if abs(time.time() - timeOrig) > timeSave * 60:
                    self.saveData()
                    timeOrig = time.time()

                if line == "Done!":
                    done = True



    def saveData(self) -> str:
        """
        saves numpy array to csv file with the option to save at different time intervals

        Returns
        -------
        fileName
            fileName for file that was just saved
        """
        
        if not os.path.exists(self.fileName):
            np.savetxt(self.fileName, self.arr, delimiter="," , fmt='%s')
            if (self.mode == "scan"):
                self.arr = np.empty([1, self.scanArrWidth], dtype="object")
            elif (self.mode == "PNO"):
                self.arr = np.empty([1, self.PNOArrWidth], dtype="object")
        else:
            with open(self.fileName,'ab') as f:
                np.savetxt(f, self.arr[1:, :], delimiter="," , fmt='%s')
            if (self.mode == "scan"):
                self.arr = np.empty([1, self.scanArrWidth], dtype="object")
            elif (self.mode == "PNO"):
                self.arr = np.empty([1, self.PNOArrWidth], dtype="object")
        print("SAVED")
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
        self.mode = "scan"

        self.parameters = "<scan," + str(SCAN_RANGE) + "," + str(SCAN_STEP_SIZE) + "," + str(SCAN_READ_COUNT) + "," + str(SCAN_RATE) + "," + str(LIGHT_STATUS) + ">"


        headerArr = ["Time","Volts_output",
                       "Pixel 0_0 V","Pixel 0_0 mA",
                       "Pixel 0_1 V","Pixel 0_1 mA",
                       "Pixel 0_2 V","Pixel 0_2 mA",
                       "Pixel 0_3 V","Pixel 0_3 mA",
                       "Pixel 0_4 V","Pixel 0_4 mA",
                       "Pixel 0_5 V","Pixel 0_5 mA",
                       "Pixel 0_6 V","Pixel 0_6 mA",
                       "Pixel 0_7 V","Pixel 0_7 mA",
                       "Pixel 1_0 V","Pixel 1_0 mA",
                       "Pixel 1_1 V","Pixel 1_1 mA",
                       "Pixel 1_2 V","Pixel 1_2 mA",
                       "Pixel 1_3 V","Pixel 1_3 mA",
                       "Pixel 1_4 V","Pixel 1_4 mA",
                       "Pixel 1_5 V","Pixel 1_5 mA",
                       "Pixel 1_6 V","Pixel 1_6 mA",
                       "Pixel 1_7 V","Pixel 1_7 mA",
                       "Pixel 2_0 V","Pixel 2_0 mA",
                       "Pixel 2_1 V","Pixel 2_1 mA",
                       "Pixel 2_2 V","Pixel 2_2 mA",
                       "Pixel 2_3 V","Pixel 2_3 mA",
                       "Pixel 2_4 V","Pixel 2_4 mA",
                       "Pixel 2_5 V","Pixel 2_5 mA",
                       "Pixel 2_6 V","Pixel 2_6 mA",
                       "Pixel 2_7 V","Pixel 2_7 mA",
                       "Pixel 3_0 V","Pixel 3_0 mA",
                       "Pixel 3_1 V","Pixel 3_1 mA",
                       "Pixel 3_2 V","Pixel 3_2 mA",
                       "Pixel 3_3 V","Pixel 3_3 mA",
                       "Pixel 3_4 V","Pixel 3_4 mA",
                       "Pixel 3_5 V","Pixel 3_5 mA",
                       "Pixel 3_6 V","Pixel 3_6 mA",
                       "Pixel 3_7 V","Pixel 3_7 mA",

                       "ARDUINOID"]

        self.scanArrWidth = len(headerArr)

        self.arr = np.empty([6, len(headerArr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", SCAN_RANGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", SCAN_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: " , SCAN_READ_COUNT
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", SCAN_RATE
        self.arr[4][0], self.arr[4][1] = "Light Status: ",  light
        self.arr[5] = headerArr
        # print(headerArr)

        self.ser.write(self.parameters.encode())  # send data to arduino
        self.readData()
        print(self.arr)
        # self.printTime()
        self.saveData()
        return self.fileName


    def pno(self, PNO_STARTING_VOLTAGE: float, PNO_STEP_SIZE: float, PNO_MEASUREMENTS_PER_STEP: int, PNO_MEASUREMENT_DELAY: int, PNO_MEASUREMENT_TIME: int) -> np.ndarray:
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
        PNO_MEASUREMENT_TIME : int
            total time to run pno for (minutes)

        Returns
        -------
        arr
            numpy array filled with data
        filename
            name of file that data will be saved to
        """

        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.fileName = "./data/PnO" + today + ".csv"
        self.mode = "PNO"

        ## TURN INPUT SECONDS INTO MINUTES
        # PNO_MEASUREMENT_TIME = PNO_MEASUREMENT_TIME*60


        self.parameters = "<PnO," + str(PNO_STARTING_VOLTAGE) + "," + str(PNO_STEP_SIZE) + "," + str(PNO_MEASUREMENTS_PER_STEP) + "," + str(PNO_MEASUREMENT_DELAY) + "," + str(PNO_MEASUREMENT_TIME) + ">"

        headerArr  = ["Time",
                       "Pixel 0_0 V","Pixel 0_0 mA",
                       "Pixel 0_1 V","Pixel 0_1 mA",
                       "Pixel 0_2 V","Pixel 0_2 mA",
                       "Pixel 0_3 V","Pixel 0_3 mA",
                       "Pixel 0_4 V","Pixel 0_4 mA",
                       "Pixel 0_5 V","Pixel 0_5 mA",
                       "Pixel 0_6 V","Pixel 0_6 mA",
                       "Pixel 0_7 V","Pixel 0_7 mA",
                       "Pixel 1_0 V","Pixel 1_0 mA",
                       "Pixel 1_1 V","Pixel 1_1 mA",
                       "Pixel 1_2 V","Pixel 1_2 mA",
                       "Pixel 1_3 V","Pixel 1_3 mA",
                       "Pixel 1_4 V","Pixel 1_4 mA",
                       "Pixel 1_5 V","Pixel 1_5 mA",
                       "Pixel 1_6 V","Pixel 1_6 mA",
                       "Pixel 1_7 V","Pixel 1_7 mA",
                       "Pixel 2_0 V","Pixel 2_0 mA",
                       "Pixel 2_1 V","Pixel 2_1 mA",
                       "Pixel 2_2 V","Pixel 2_2 mA",
                       "Pixel 2_3 V","Pixel 2_3 mA",
                       "Pixel 2_4 V","Pixel 2_4 mA",
                       "Pixel 2_5 V","Pixel 2_5 mA",
                       "Pixel 2_6 V","Pixel 2_6 mA",
                       "Pixel 2_7 V","Pixel 2_7 mA",
                       "Pixel 3_0 V","Pixel 3_0 mA",
                       "Pixel 3_1 V","Pixel 3_1 mA",
                       "Pixel 3_2 V","Pixel 3_2 mA",
                       "Pixel 3_3 V","Pixel 3_3 mA",
                       "Pixel 3_4 V","Pixel 3_4 mA",
                       "Pixel 3_5 V","Pixel 3_5 mA",
                       "Pixel 3_6 V","Pixel 3_6 mA",
                       "Pixel 3_7 V","Pixel 3_7 mA",
                       "Pixel 0_0 PCE",
                       "Pixel 0_1 PCE",
                       "Pixel 0_2 PCE",
                       "Pixel 0_3 PCE",
                       "Pixel 0_4 PCE",
                       "Pixel 0_5 PCE",
                       "Pixel 0_6 PCE",
                       "Pixel 0_7 PCE",
                       "Pixel 1_0 PCE",
                       "Pixel 1_1 PCE",
                       "Pixel 1_2 PCE",
                       "Pixel 1_3 PCE",
                       "Pixel 1_4 PCE",
                       "Pixel 1_5 PCE",
                       "Pixel 1_6 PCE",
                       "Pixel 1_7 PCE",
                       "Pixel 2_0 PCE",
                       "Pixel 2_1 PCE",
                       "Pixel 2_2 PCE",
                       "Pixel 2_3 PCE",
                       "Pixel 2_4 PCE",
                       "Pixel 2_5 PCE",
                       "Pixel 2_6 PCE",
                       "Pixel 2_7 PCE",
                       "Pixel 3_0 PCE",
                       "Pixel 3_1 PCE",
                       "Pixel 3_2 PCE",
                       "Pixel 3_3 PCE",
                       "Pixel 3_4 PCE",
                       "Pixel 3_5 PCE",
                       "Pixel 3_6 PCE",
                       "Pixel 3_7 PCE",
                       "ARDUINOID"]

        self.PNOArrWidth = len(headerArr)

        self.arr = np.empty([6, len(headerArr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", PNO_STARTING_VOLTAGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", PNO_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: ", PNO_MEASUREMENTS_PER_STEP
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", PNO_MEASUREMENT_DELAY
        self.arr[4][0], self.arr[4][1] = "Voltage Measurement Time: ", PNO_MEASUREMENT_TIME
        self.arr[5] = headerArr
        # print(headerArr)

        print(self.parameters)
        self.ser.write(self.parameters.encode())  # send data to arduino
        self.readData()
        print(self.arr)
        self.printTime()
        self.saveData()

        return self.fileName