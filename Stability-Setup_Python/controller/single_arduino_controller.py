# single_arduino_controller.py
#!/usr/bin/env python3
from email import header
from fileinput import filename
from constants import Mode, ConstantsController
from data_visualization import data_plotter
from helper.global_helpers import custom_print
import serial
import time
from datetime import datetime
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import threading
import logging

class single_controller:

    def __init__(
        self,
        COM: str,
        SERIAL_BAUD_RATE: int,
        trial_name: str,
        date: str,
        folder_path: str,
    ) -> None:
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
        self.reading_lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.should_run = True
        self.baud_rate = SERIAL_BAUD_RATE

        self.mode = ""
        self.scan_filename = ""
        self.file_name = ""

        self.arduinoID = None
        self.trial_name = ""
        if trial_name:
            self.trial_name = trial_name + " "
        self.today = date
        self.folder_path = folder_path
        self.start = time.time()

        self.scan_arr_width = 0
        self.pno_arr_width = 0

    def connect(self):
        try:
            # self.ser = serial.Serial(self.port, self.baud_rate)
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            self.reset_arduino()

            time.sleep(0.5)
            done = False
            while not done:
                with self.reading_lock:
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    custom_print(f"Pre-Init Stage Arduino {self.arduinoID} Output:", line)
                    if "HW_ID" in line:
                        HW_ID = line.split(":")[-1]
                        self.arduinoID = ConstantsController.arduino_ID[HW_ID]
                        print(self.arduinoID)
                    if "Arduino Ready" in line:
                        done = True
            self.ser.reset_input_buffer()

        except serial.SerialException as e:
            custom_print(f"Failed to connect to {self.port}. Error: {e}")
            return False
        return True

    def scan(self, params):
        SCAN_RANGE = float(params[0])
        SCAN_STEP_SIZE = float(params[1])
        SCAN_READ_COUNT = int(params[2])
        SCAN_RATE = int(params[3])
        LIGHT_STATUS = int(params[4])
        custom_print("Scan Initiated")

        if LIGHT_STATUS == 0:
            light_status = "dark"
        else:
            light_status = "light"

        self.file_name = (
            self.folder_path
            + self.trial_name
            + self.today
            + light_status
            + "ID"
            + self.arduinoID
            + "scan.csv"
        )
        self.mode = Mode.SCAN
        self.parameters = (
            "scan,"
            + str(SCAN_RANGE)
            + ","
            + str(SCAN_STEP_SIZE)
            + ","
            + str(SCAN_READ_COUNT)
            + ","
            + str(SCAN_RATE)
            + ","
            + str(LIGHT_STATUS)
            + ""
        )

        custom_print(f"Parameters: {self.parameters}")
        self._start_scan(
            SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status
        )
        self._read_data()
        if os.path.exists(self.file_name):
            data_plotter.create_graph(os.path.abspath(self.file_name))
        else:
            custom_print("File Not Found")

    def _start_scan(
        self, SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, LIGHT_STATUS
    ):
        custom_print("Starting Scan")
        if not self.should_run: custom_print("Run Blocked")

        voltage_lambda = lambda value: "Pixel_" + str(value + 1) + " V"
        amperage_lambda = lambda value: "Pixel_" + str(value + 1) + " mA"
        header_arr = ["Time", "Voltage_Applied"]
        sent = False
        received = False
        line = ""

        while self.should_run and not sent:
            try:
                with self.write_lock:
                    self.ser.write(self.parameters.encode())  # send data to arduino
                    custom_print(f"Sent Scan Start Command {self.parameters}")
                    sent = True
            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                break

        while self.should_run and not received:
            try:
                with self.reading_lock:
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    custom_print(f"INIT STAGE ARDUINO {self.arduinoID} OUTPUT:", line)
                    if "Measurement Started" in line:
                        header_arr.extend(
                            [
                                f(value)
                                for value in range(8)
                                for f in (voltage_lambda, amperage_lambda)
                            ]
                        )
                        received = True
            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                break

        header_arr.append("ARUDUINOID")

        self.scan_arr_width = len(header_arr)

        self.arr = np.empty([7, len(header_arr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range: ", SCAN_RANGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size: ", SCAN_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = "Voltage Read Count: ", SCAN_READ_COUNT
        self.arr[3][0], self.arr[3][1] = "Voltage Delay Time: ", SCAN_RATE
        self.arr[4][0], self.arr[4][1] = "Light Status: ", LIGHT_STATUS
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = header_arr

    def constant_voltage(self, params):
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
        self.file_name = (
            self.folder_path
            + self.trial_name
            + self.today
            + light_status
            + "ID"
            + self.arduinoID
            + "constant_voltage.csv"
        )
        custom_print("constant voltage started")

        self.parameters = (
            "constantVoltage,"
            + str(SCAN_RANGE)
            + ","
            + str(SCAN_STEP_SIZE)
            + ","
            + str(SCAN_READ_COUNT)
            + ","
            + str(SCAN_RATE)
            + ","
            + str(LIGHT_STATUS)
            + ""
        )

        custom_print(f"Parameters: {self.parameters}")
        self._start_scan(
            SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status
        )
        self._read_data()

    def pno(self, scan_file_name, params):
        PNO_STARTING_VOLTAGE = float(params[0])
        PNO_STEP_SIZE = float(params[1])
        PNO_MEASUREMENTS_PER_STEP = int(params[2])
        PNO_MEASUREMENT_DELAY = int(params[3])
        PNO_MEASUREMENT_TIME = int(params[4])
        self.file_name = (
            self.folder_path
            + self.trial_name
            + self.today
            + "ID"
            + self.arduinoID
            + "PnO.csv"
        )
        self.scan_filename = scan_file_name
        self.mode = Mode.MPPT

        # if self.scan_filename:
        #     VMPP = self.find_vmpp(scan_file_name)
        #     custom_print(f"PC: VMPP-> {VMPP}")

        # VMPP = "0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6"
        # TODO: reimplement vmpp
        self.parameters = (
            "PnO,"
            + str(PNO_STARTING_VOLTAGE)
            + ","
            + str(PNO_STEP_SIZE)
            + ","
            + str(PNO_MEASUREMENTS_PER_STEP)
            + ","
            + str(PNO_MEASUREMENT_DELAY)
            + ","
            + str(PNO_MEASUREMENT_TIME)
        )

        custom_print(f"Parameters:  {self.parameters}")
        self._start_pno(
            PNO_STARTING_VOLTAGE,
            PNO_STEP_SIZE,
            PNO_MEASUREMENTS_PER_STEP,
            PNO_MEASUREMENT_DELAY,
            PNO_MEASUREMENT_TIME,
        )
        custom_print(self.file_name)
        self._read_data()
        data_plotter.create_graph(os.path.abspath(self.file_name))

    def _start_pno(
        self,
        PNO_STARTING_VOLTAGE,
        PNO_STEP_SIZE,
        PNO_MEASUREMENTS_PER_STEP,
        PNO_MEASUREMENT_DELAY,
        PNO_MEASUREMENT_TIME,
    ):

        voltage_lambda = lambda value: "Pixel_" + str(value + 1) + " V"
        amperage_lambda = lambda value: "Pixel_" + str(value + 1) + " mA"
        power_lambda = lambda y: "Pixel_" + str(y) + " PCE"
        header_arr = ["Time"]
        pce_header = []

        done = False
        line = ""
        while self.should_run and not done:
            try:
                with self.write_lock:
                    self.ser.write(self.parameters.encode())  # send data to arduino
                    line = self.ser.readline().decode().strip()
                    data_list = line.split(",")
                    custom_print(f"INIT Arduino {self.arduinoID}", data_list)
                    if "Measurement Started" in line:
                        header_arr.extend(
                            [
                                f(value)
                                for value in range(8)
                                for f in (voltage_lambda, amperage_lambda)
                            ]
                        )
                        pce_header.extend(
                            [
                                power_lambda(value)
                                for value in range(8)
                            ]
                        )
                        done = True
            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                break

        header_arr.extend(pce_header)
        header_arr.append("ARUDUINOID")

        self.pno_arr_width = len(header_arr)
        self.arr = np.empty([7, len(header_arr)], dtype="object")
        self.arr[0][0], self.arr[0][1] = "Voltage Range (V): ", PNO_STARTING_VOLTAGE
        self.arr[1][0], self.arr[1][1] = "Voltage Step Size (V): ", PNO_STEP_SIZE
        self.arr[2][0], self.arr[2][1] = (
            "Voltage Read Count: ",
            PNO_MEASUREMENTS_PER_STEP,
        )
        self.arr[3][0], self.arr[3][1] = (
            "Voltage Delay Time (ms): ",
            PNO_MEASUREMENT_DELAY,
        )
        self.arr[4][0], self.arr[4][1] = (
            "Voltage Measurement Time (Hrs): ",
            PNO_MEASUREMENT_TIME,
        )
        self.arr[5][0], self.arr[5][1] = "Start Date: ", self.today
        # self.arr[6][0], self.arr[6][1] = "End Date: ", datetime.now().strftime("%b-%d-%Y")
        self.arr[6] = header_arr

    def reset_arduino(self):
        """
        Resets the specified Arduino by toggling the DTR signal.
        """
        try:
            if self.ser and self.ser.is_open:
                self.ser.setDTR(False)
                time.sleep(0.1)  # Wait for 100ms
                self.ser.setDTR(True)
                print(f"Arduino has been reset.")
            else:
                print(f"Arduino is not connected.")
        except Exception as e:
            print(f"Failed to reset Arduino: {e}")

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
                with self.reading_lock:
                    line = self.ser.readline().decode("unicode_escape").rstrip()
                    data_list = line.split(",")
                    if len(data_list) > 0:
                        # custom_print(data_list)

                        custom_print(f"ARDUINO{self.arduinoID}: {line}")

                        if len(data_list) > 10:
                            self.arr = np.append(
                                self.arr, np.array([data_list], dtype="object"), axis=0
                            )

                        if (
                            abs(time.time() - time_orig)
                            > ConstantsController.save_time
                        ):
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
                custom_print(f"Communication error on {self.port}. Error: {e}")
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
            np.savetxt(self.file_name, self.arr, delimiter=",", fmt="%s")
            if self.mode == Mode.SCAN:
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif self.mode == Mode.MPPT:
                self.arr = np.empty([1, self.pno_arr_width], dtype="object")
        else:
            with open(self.file_name, "ab") as f:
                np.savetxt(f, self.arr[1:, :], delimiter=",", fmt="%s")
            if self.mode == Mode.SCAN:
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif self.mode == Mode.MPPT:
                self.arr = np.empty([1, self.pno_arr_width], dtype="object")

        custom_print("SAVED")

    def set_folder_path(self, new_folder_path):
        self.folder_path = new_folder_path

    def find_vmpp(self, scan_file_name):
        arr = np.loadtxt(scan_file_name, delimiter=",", dtype=str)
        scan_file_name = scan_file_name.split("\\")
        # custom_print(arr)
        headers = arr[6, :]
        headerDict = {value: index for index, value in enumerate(headers)}
        # custom_print(headerDict)
        arr = arr[7:, :]
        length = len(headers) - 1
        # custom_print(length)

        jv_list = []

        for i in range(2, length):
            jv_list.append(arr[:, i])

        j_list = []  # current
        v_list = []  # voltage
        for i in range(0, len(jv_list), 2):
            # custom_print(i)
            j_list.append([float(j) for j in jv_list[i + 1]])
            v_list.append([float(x) for x in jv_list[i]])
            # jv_list[i+1] = [float(x) / 0.128 for x in jv_list[i+1]]

        j_list = np.array(j_list).T
        v_list = np.array(v_list).T
        pceList = j_list * v_list
        vmpp_encode_string = ""
        max_V_idx = np.argmax(pceList, axis=0)  # find index of max pce value

        for i in range(len(max_V_idx) - 1):
            vmpp_encode_string += (
                str(v_list[max_V_idx[i], i]) + ","
            )  # v_list is 84x32, vmaxIDx contains the i in 84 that is the best voltage per pixel

        vmpp_encode_string += str(
            v_list[max_V_idx[len(max_V_idx) - 1], len(max_V_idx) - 1]
        )

        return vmpp_encode_string

    def printTime(self):
        end = time.time()
        total_time = end - self.start
        custom_print("\n" + str(total_time))


def find_vmpp(scan_file_name):

    arr = np.loadtxt(scan_file_name, delimiter=",", dtype=str)
    scan_file_name = scan_file_name.split("\\")
    # custom_print(arr)
    headers = arr[6, :]
    headerDict = {value: index for index, value in enumerate(headers)}
    # custom_print(headerDict)
    arr = arr[7:, :]
    length = len(headers) - 1
    # custom_print(length)

    jv_list = []

    for i in range(2, length):
        jv_list.append(arr[:, i])

    j_list = []  # current
    v_list = []  # voltage
    for i in range(0, len(jv_list), 2):
        # custom_print(i)
        j_list.append([float(j) for j in jv_list[i + 1]])
        v_list.append([float(x) for x in jv_list[i]])
        # jv_list[i+1] = [float(x) / 0.128 for x in jv_list[i+1]]

    j_list = np.array(j_list).T
    v_list = np.array(v_list).T
    pceList = j_list * v_list
    vmpp_encode_string = ""
    max_V_idx = np.argmax(pceList, axis=0)  # find index of max pce value

    for i in range(len(max_V_idx) - 1):
        vmpp_encode_string += (
            str(v_list[max_V_idx[i], i]) + ","
        )  # v_list is 84x32, vmaxIDx contains the i in 84 that is the best voltage per pixel

    vmpp_encode_string += str(v_list[max_V_idx[len(max_V_idx) - 1], len(max_V_idx) - 1])

    return vmpp_encode_string


if __name__ == "__main__":
    # scan_calcs(".\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.csv")
    custom_print(
        find_vmpp(
            r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Oct-27-2023 17_18_16\Oct-27-2023 17_18_26lightID0scan.csv"
        )
    )
