#!/usr/bin/env python3
from email import header
from fileinput import filename
from constants_1_0 import Mode, constants_controller
from data_visualization import data_show_1_0
import serial
import time
from datetime import datetime
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import threading
import logging
log_name = "controller"

class controller:

    # def __init__(self) -> None:
    #     pass

    def __init__(self, arduinoID: int, COM: str, SERIAL_BAUD_RATE: int, folder_path: str, today: str) -> None:
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
        self.port = COM
        self.ser = None
        self.lock = threading.Lock()
        self.should_run = True
        self.baud_rate = SERIAL_BAUD_RATE

        self.mode = ""
        self.scan_filename = ""
        self.file_name = ""

        self.arduinoID = str(arduinoID)
        self.today = today
        self.folder_path = folder_path
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        self.start = time.time()

        self.scan_arr_width = 0
        self.pno_arr_width = 0

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate)
            # self.ser.flush()
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}. Error: {e}")
            return False
        return True

    def multithreaded_scan(self, params, return_arr):
        SCAN_RANGE = float(params[0])
        SCAN_STEP_SIZE = float(params[1])
        SCAN_READ_COUNT = int(params[2])
        SCAN_RATE = int(params[3])
        LIGHT_STATUS = int(params[4])
        print("scan started")

        if LIGHT_STATUS == 0:
            light_status = "dark"
        else:
            light_status = "light"

        self.file_name = (self.folder_path +
                        datetime.now().strftime("%b-%d-%Y %H_%M_%S") +
                        light_status + "ID" + self.arduinoID +
                        "scan.csv")
        self.mode = Mode.SCAN
        self.parameters = ("<scan," +
                        str(SCAN_RANGE) + "," +
                        str(SCAN_STEP_SIZE) + "," +
                        str(SCAN_READ_COUNT) + "," +
                        str(SCAN_RATE) + "," +
                        str(LIGHT_STATUS) + ">")

        print(f"PC: {self.parameters}")
        self._start_scan(SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status)
        self._read_data()
        return_arr.append(str(os.path.abspath(self.file_name)))

    def multithreaded_constant_voltage(self, params, return_arr):
        SCAN_RANGE = float(params[0])
        SCAN_STEP_SIZE = 0.1
        SCAN_READ_COUNT = 1
        SCAN_RATE = 0
        LIGHT_STATUS = 0
        if LIGHT_STATUS == 0:
            light_status = "dark"
        else:
            light_status = "light"
        self.mode = Mode.SCAN
        self.file_name = (self.folder_path +
                        datetime.now().strftime("%b-%d-%Y %H_%M_%S") +
                        light_status + "ID" + self.arduinoID +
                        "constant_voltage.csv")
        print("constant voltage started")

        self.parameters = ("<constantVoltage," +
                        str(SCAN_RANGE) + "," +
                        str(SCAN_STEP_SIZE) + "," +
                        str(SCAN_READ_COUNT) + "," +
                        str(SCAN_RATE) + "," +
                        str(LIGHT_STATUS) + ">")

        print(f"PC: {self.parameters}")
        self._start_scan(SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status)
        self._read_data()
        return_arr.append(str(os.path.abspath(self.file_name)))

    def multithreaded_pno(self, scan_file_name, params, return_arr):
        PNO_STARTING_VOLTAGE = float(params[0])
        PNO_STEP_SIZE = float(params[1])
        PNO_MEASUREMENTS_PER_STEP = int(params[2])
        PNO_MEASUREMENT_DELAY = int(params[3])
        PNO_MEASUREMENT_TIME = int(params[4])
        self.file_name = (self.folder_path +
                            datetime.now().strftime("%b-%d-%Y %H_%M_%S") +
                            "ID" + self.arduinoID +
                            "PnO.csv")
        self.scan_filename = scan_file_name
        self.mode = Mode.PNO

        # if self.scan_filename:
        #     VMPP = self.find_vmpp(scan_file_name)
        #     print(f"PC: VMPP-> {VMPP}")

        VMPP = "<0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6>"

        # VMPP = "<0.7148,0.6797,0.5118,0.2118,0.4197,0.7367,0.3238,0.5358,0.7077,1.092,0.6237,0.5957,0.82,0.913,0.676,0.6437,0.7076,0.5567,0.7357,0.1439,0.6436,-0.0,0.6666,0.6438,0.4729,0.5639,0.6069,0.0,0.1189,0.2299,0.752,1.096>"
        self.parameters = ("<PnO," +
                           str(PNO_STARTING_VOLTAGE) + "," +
                           str(PNO_STEP_SIZE) + "," +
                           str(PNO_MEASUREMENTS_PER_STEP) + "," +
                           str(PNO_MEASUREMENT_DELAY) + "," +
                           str(PNO_MEASUREMENT_TIME) + "," +
                           VMPP + ">")

        print(f"PC -> Arduino:  {self.parameters}", log_name)
        self._start_pno(PNO_STARTING_VOLTAGE,
                           PNO_STEP_SIZE,
                           PNO_MEASUREMENTS_PER_STEP,
                           PNO_MEASUREMENT_DELAY,
                           PNO_MEASUREMENT_TIME)
        print("PC ->", self.file_name)
        self._read_data()
        return_arr.append(str(os.path.abspath(self.file_name)))

    def stop(self):
        self.should_run = False
        with self.lock:
            if self.ser:
                self.ser.close()

    def _read_data(self):
        """
        - Reads data outputed on serial bus by arduino
        - Saves data after certain interval of time
        - Does not need to manage mode because that is taken care of on the arduino
        """
        done = False
        line = ""
        time_orig = time.time()

        while self.should_run and not done:
            try:
                with self.lock:
                    line = self.ser.readline().decode('unicode_escape').rstrip()
                    data_list = line.split(",")
                    if len(data_list) > 0:
                        # print(data_list)

                        print(f"ARDUINO{self.arduinoID}: {line}")

                        if len(data_list) > 10:
                            self.arr = np.append(self.arr, np.array([data_list], dtype='object'),axis = 0)

                        if abs(time.time() - time_orig) > constants_controller["save_time"]:
                            self._save_data()
                            time_orig = time.time()

                        # if self.mode == "PNO" and abs(time.time() - pno_time_org) > pno_time_save * 60:
                        #     self._gen_pno_graphs(str(os.path.abspath(self.file_name)), self.scan_filename)
                        #     pno_time_org = time.time()
                        if line == "Done!":
                            self._save_data()
                            self.ser.flush()
                            done = True

            except serial.SerialException as e:
                print(f"Communication error on {self.port}. Error: {e}")
                break

    def _save_data(self) -> str:
        """
        - saves numpy array to csv file with the option to save at different time intervals
        - wipes self.arr to reduce memory usage

        Returns
        -------
        file_name
            file_name for file that was just saved
        """
        if not os.path.exists(self.file_name):
            np.savetxt(self.file_name, self.arr, delimiter="," , fmt='%s')
            if (self.mode == Mode.SCAN):
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif (self.mode == Mode.PNO):
                self.arr = np.empty([1, self.pno_arr_width], dtype="object")
        else:
            with open(self.file_name,'ab') as f:
                np.savetxt(f, self.arr[1:, :], delimiter="," , fmt='%s')
            if (self.mode == Mode.SCAN):
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif (self.mode == Mode.PNO):
                self.arr = np.empty([1, self.pno_arr_width], dtype="object")

        # if (self.mode == Mode.PNO):
        #     data_show_1_0.show_pce_graphs_one_graph(self.file_name, show_dead_pixels = True, pixels= None, devices= None)
        print("PC: SAVED", log_name)

    def _start_pno(self, PNO_STARTING_VOLTAGE,
                      PNO_STEP_SIZE, PNO_MEASUREMENTS_PER_STEP,
                      PNO_MEASUREMENT_DELAY, PNO_MEASUREMENT_TIME):

        voltage_lambda = lambda x, y : "Pixel " + str(x+1) + "_" + str(y+1) + " V"
        amperage_lambda = lambda x, y : "Pixel " + str(x+1) + "_" + str(y+1) + " mA"
        header_arr = ["Time"]
        pce_header = []

        done = False
        line = ""
        while self.should_run and not done:
            try:
                with self.lock:
                    self.ser.write(self.parameters.encode())    # send data to arduino
                    line = self.ser.readline().decode().strip()
                    data_list = line.split(",")
                    print(f"INIT Arduino {self.arduinoID}", data_list)
                    if len(data_list) > 10:
                        pixels_total = int((len(data_list)-2)/24)
                        for i in range(pixels_total):
                            header_arr.extend([f(i, x) for x in range(8) for f in (voltage_lambda, amperage_lambda)])
                            pce_header.extend(["Pixel " + str(i) + "_" + str(value) + " PCE" for value in range(8)])
                        done = True
            except serial.SerialException as e:
                print(f"Communication error on {self.port}. Error: {e}")
                break


        header_arr.extend(pce_header)
        header_arr.append("ARUDUINOID")


        self.pno_arr_width = len(header_arr)
        self.arr = np.empty([7, len(header_arr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range (V): ", PNO_STARTING_VOLTAGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size (V): ", PNO_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: ", PNO_MEASUREMENTS_PER_STEP
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time (ms): ", PNO_MEASUREMENT_DELAY
        self.arr[4][0], self.arr[4][1] = "Voltage Measurement Time (Hrs): ", PNO_MEASUREMENT_TIME
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = header_arr
        self.arr = np.append(self.arr, np.array([data_list]),axis = 0)

    def _start_scan(self, SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, LIGHT_STATUS):
        voltage_lambda = lambda x, y : "Pixel " + str(x+1) + "_" + str(y+1) + " V"
        amperage_lambda = lambda x, y : "Pixel " + str(x+1) + "_" + str(y+1) + " mA"
        header_arr = ["Time", "Voltage_Applied"]
        done = False
        line = ""

        while self.should_run and not done:
            try:
                with self.lock:
                    self.ser.write(self.parameters.encode())  # send data to arduino
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    data_list = line.split(",")
                    print(f"INIT Arduino {self.arduinoID}", data_list)
                    if len(data_list) > 10:
                        pixels_total = int((len(data_list)-2)/16)
                        for i in range(pixels_total):
                            header_arr.extend([f(i, x) for x in range(8) for f in (voltage_lambda, amperage_lambda)])
                        done = True
            except serial.SerialException as e:
                print(f"Communication error on {self.port}. Error: {e}")
                break

        header_arr.append("ARUDUINOID")

        self.scan_arr_width = len(header_arr)

        self.arr = np.empty([7, len(header_arr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", SCAN_RANGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", SCAN_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: " , SCAN_READ_COUNT
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", SCAN_RATE
        self.arr[4][0], self.arr[4][1] = "Light Status: ",  LIGHT_STATUS
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = header_arr
        self.arr = np.append(self.arr, np.array([data_list]),axis = 0)

    def set_folder_path(self, new_folder_path):
        self.folder_path = new_folder_path

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
        file_name
            name of file that data will be saved to
        """
        print("scan started")

        if LIGHT_STATUS == 0:
            light_status = "dark"
        else:
            light_status = "light"

        self.file_name = (self.folder_path +
                          datetime.now().strftime("%b-%d-%Y %H_%M_%S") +
                          light_status + "ID" + self.arduinoID +
                          "scan.csv")
        self.mode = Mode.SCAN
        self.parameters = ("<scan," +
                           str(SCAN_RANGE) + "," +
                           str(SCAN_STEP_SIZE) + "," +
                           str(SCAN_READ_COUNT) + "," +
                           str(SCAN_RATE) + "," +
                           str(LIGHT_STATUS) + ">")

        print(f"PC: {self.parameters}")
        self.ser.write(b"<scan,1.2,0.03,2,50,1>")  # send data to arduino
        self._start_scan(SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status)
        # print("PC: ", self.arr)
        self._read_data()
        return str(os.path.abspath(self.file_name))


        # print(self.arr)
        # self.printTime()
        # self._save_data()



    def pno(self, PNO_STARTING_VOLTAGE: float,
            PNO_STEP_SIZE: float, PNO_MEASUREMENTS_PER_STEP: int,
            PNO_MEASUREMENT_DELAY: int, PNO_MEASUREMENT_TIME:
            int, scan_file_name: str) -> np.ndarray:
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
        file_name
            name of file that data will be saved to
        """
        self.file_name = (self.folder_path +
                            datetime.now().strftime("%b-%d-%Y %H_%M_%S") +
                            "ID" + self.arduinoID +
                            "PnO.csv")
        self.scan_filename = scan_file_name
        self.mode = Mode.PNO
        VMPP = self.find_vmpp(scan_file_name)

        # VMPP = "<0.7148,0.6797,0.5118,0.2118,0.4197,0.7367,0.3238,0.5358,0.7077,1.092,0.6237,0.5957,0.82,0.913,0.676,0.6437,0.7076,0.5567,0.7357,0.1439,0.6436,-0.0,0.6666,0.6438,0.4729,0.5639,0.6069,0.0,0.1189,0.2299,0.752,1.096>"
        self.parameters = ("<PnO," +
                           str(PNO_STARTING_VOLTAGE) + "," +
                           str(PNO_STEP_SIZE) + "," +
                           str(PNO_MEASUREMENTS_PER_STEP) + "," +
                           str(PNO_MEASUREMENT_DELAY) + "," +
                           str(PNO_MEASUREMENT_TIME) + "," +
                           VMPP + ">")

        print(f"PC -> Arduino:  {self.parameters}", log_name)
        self.ser.write(self.parameters.encode())    # send data to arduino
        # self.ser.write(VMPP.encode())               # send pno starting voltages to arduino

        self._start_pno(PNO_STARTING_VOLTAGE,
                           PNO_STEP_SIZE,
                           PNO_MEASUREMENTS_PER_STEP,
                           PNO_MEASUREMENT_DELAY,
                           PNO_MEASUREMENT_TIME)

        self._read_data()

        return str(os.path.abspath(self.file_name))

    def find_vmpp(self, scan_file_name):
        arr = np.loadtxt(scan_file_name, delimiter=",", dtype=str)
        scan_file_name = scan_file_name.split('\\')
        # print(arr)
        headers = arr[6,:]
        headerDict = {value: index for index, value in enumerate(headers)}
        # print(headerDict)
        arr = arr[7:, :]
        length = (len(headers) - 1)
        # print(length)

        jv_list = []

        for i in range(2, length):
            jv_list.append(arr[:,i])

        j_list = [] #current
        v_list = [] #voltage
        for i in range(0,len(jv_list),2):
            # print(i)
            j_list.append([float(j) for j in jv_list[i+1]])
            v_list.append([float(x) for x in jv_list[i]])
            # jv_list[i+1] = [float(x) / 0.128 for x in jv_list[i+1]]


        j_list = np.array(j_list).T
        v_list = np.array(v_list).T
        pceList = j_list*v_list
        vmpp_encode_string = ""
        max_V_idx = np.argmax(pceList, axis=0) # find index of max pce value

        for i in range(len(max_V_idx)-1):
            vmpp_encode_string += str(v_list[max_V_idx[i],i]) + "," # v_list is 84x32, vmaxIDx contains the i in 84 that is the best voltage per pixel

        vmpp_encode_string += str(v_list[max_V_idx[len(max_V_idx)-1],len(max_V_idx)-1])

        return vmpp_encode_string

    def printTime(self):
        end = time.time()
        total_time = end - self.start
        print("\n"+ str(total_time))

def find_vmpp(scan_file_name):

        arr = np.loadtxt(scan_file_name, delimiter=",", dtype=str)
        scan_file_name = scan_file_name.split('\\')
        # print(arr)
        headers = arr[6,:]
        headerDict = {value: index for index, value in enumerate(headers)}
        # print(headerDict)
        arr = arr[7:, :]
        length = (len(headers) - 1)
        # print(length)

        jv_list = []

        for i in range(2, length):
            jv_list.append(arr[:,i])

        j_list = [] #current
        v_list = [] #voltage
        for i in range(0,len(jv_list),2):
            # print(i)
            j_list.append([float(j) for j in jv_list[i+1]])
            v_list.append([float(x) for x in jv_list[i]])
            # jv_list[i+1] = [float(x) / 0.128 for x in jv_list[i+1]]


        j_list = np.array(j_list).T
        v_list = np.array(v_list).T
        pceList = j_list*v_list
        vmpp_encode_string = ""
        max_V_idx = np.argmax(pceList, axis=0) # find index of max pce value

        for i in range(len(max_V_idx)-1):
            vmpp_encode_string += str(v_list[max_V_idx[i],i]) + "," # v_list is 84x32, vmaxIDx contains the i in 84 that is the best voltage per pixel

        vmpp_encode_string += str(v_list[max_V_idx[len(max_V_idx)-1],len(max_V_idx)-1])

        return vmpp_encode_string



if __name__ == '__main__':
    # scan_calcs(".\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.csv")
    print(find_vmpp(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Oct-27-2023 17_18_16\Oct-27-2023 17_18_26lightID0scan.csv"))




