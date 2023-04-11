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

# self.today =

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
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.folderPath = "./data/" + self.today + "/"
        if not os.path.exists(self.folderPath):
            os.mkdir(self.folderPath)
        self.start = time.time()


    def readData(self):
        """
        * Reads data outputed on serial bus by arduino
        * Saves data after certain interval of time to prevent ram overusage on lower end systems
        * Does not need to manage mode because that is taken care of on the arduino
        """
        done = False
        line = ""
        timeOrig = time.time()
        timeSave = 3 # time between saves in minutes
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
                    self.saveData()
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

        if LIGHT_STATUS == 0:
            lightStatus = "dark"
        else:
            lightStatus = "light"

        self.fileName = self.folderPath + datetime.now().strftime("%b-%d-%Y %H_%M_%S") + lightStatus + "scan.csv"

        self.mode = "scan"

        self.parameters = "<scan," + str(SCAN_RANGE) + "," + str(SCAN_STEP_SIZE) + "," + str(SCAN_READ_COUNT) + "," + str(SCAN_RATE) + "," + str(LIGHT_STATUS) + ",0.7148,0.6797,0.5118,0.2118,0.4197,0.7367,0.3238,0.5358,0.7077,1.092,0.6237,0.5957,0.82,0.913,0.676,0.6437,0.7076,0.5567,0.7357,0.1439,0.6436,-0.0,0.6666,0.6438,0.4729,0.5639,0.6069,0.0,0.1189,0.2299,0.752,1.096>"


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
        self.arr[4][0], self.arr[4][1] = "Light Status: ",  lightStatus
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = headerArr
        # print(headerArr)

        self.ser.write(self.parameters.encode())  # send data to arduino
        self.readData()
        print(self.arr)
        self.printTime()
        # self.saveData()
        return self.fileName


    def pno(self, PNO_STARTING_VOLTAGE: float, PNO_STEP_SIZE: float, PNO_MEASUREMENTS_PER_STEP: int, PNO_MEASUREMENT_DELAY: int, PNO_MEASUREMENT_TIME: int, SCAN_FILE_NAME: str) -> np.ndarray:
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
        SCAN_FILE_NAME: str
            string for file name of scan file to take VMPP from

        Returns
        -------
        arr
            numpy array filled with data
        filename
            name of file that data will be saved to
        """
        self.fileName = self.folderPath + datetime.now().strftime("%b-%d-%Y %H_%M_%S") + "scan.csv"
        # self.fileName = "./data/PnO" + self.today + ".csv"
        self.mode = "PNO"

        self.parameters = "<PnO," + str(PNO_STARTING_VOLTAGE) + "," + str(PNO_STEP_SIZE) + "," + str(PNO_MEASUREMENTS_PER_STEP) + "," + str(PNO_MEASUREMENT_DELAY) + "," + str(PNO_MEASUREMENT_TIME) + ","

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
        self.arr[0][0], self.arr[0][1] = "Voltage Range (V): ", PNO_STARTING_VOLTAGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size (V): ", PNO_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: ", PNO_MEASUREMENTS_PER_STEP
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time (ms): ", PNO_MEASUREMENT_DELAY
        self.arr[4][0], self.arr[4][1] = "Voltage Measurement Time (Hrs): ", PNO_MEASUREMENT_TIME
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = headerArr
        # print(headerArr)


        VMPP = self.findVmpp(SCAN_FILE_NAME)
        # VMPP = "<0.7148,0.6797,0.5118,0.2118,0.4197,0.7367,0.3238,0.5358,0.7077,1.092,0.6237,0.5957,0.82,0.913,0.676,0.6437,0.7076,0.5567,0.7357,0.1439,0.6436,-0.0,0.6666,0.6438,0.4729,0.5639,0.6069,0.0,0.1189,0.2299,0.752,1.096>"
        self.parameters += VMPP
        print(self.parameters)


        self.ser.write(self.parameters.encode())    # send data to arduino
        self.ser.write(VMPP.encode())               # send pno starting voltages to arduino
        self.readData()
        print(self.arr)
        self.printTime()
        # self.saveData()

        return self.fileName

def findVmpp(scanFileName):

    arr = np.loadtxt(scanFileName, delimiter=",", dtype=str)
    scanFileName = scanFileName.split('\\')
    # print(arr)
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[6:, :]
    length = (len(headers) - 1)
    # print(length)

    jvList = []

    for i in range(2, length):
        jvList.append(arr[:,i])

    jList = [] #current
    vList = [] #voltage
    for i in range(0,len(jvList),2):
        # print(i)
        jList.append([float(j) for j in jvList[i+1]])
        vList.append([float(x) for x in jvList[i]])
        # jvList[i+1] = [float(x) / 0.128 for x in jvList[i+1]]


    jList = np.array(jList).T
    vList = np.array(vList).T
    pceList = jList*vList
    VMPPEncodeString = ""
    maxVIdx = np.argmax(pceList, axis=0) # find index of max pce value

    for i in range(len(maxVIdx)-1):
        VMPPEncodeString += str(vList[maxVIdx[i],i]) + "," # vList is 84x32, vmaxIDx contains the i in 84 that is the best voltage per pixel

    VMPPEncodeString += str(vList[maxVIdx[len(maxVIdx)-1],len(maxVIdx)-1]) + ">" # proper encoding for string to send to arduino

    return VMPPEncodeString

    def printTime(self):
        end = time.time()
        total_time = end - self.start
        print("\n"+ str(total_time))




if __name__ == '__main__':
    # scanCalcs(".\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.csv")
    print(findVmpp(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Mar-15-2023\scandarkMar-15-2023 13_34_51.csv"))



