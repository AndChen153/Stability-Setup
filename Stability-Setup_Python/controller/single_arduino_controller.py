# single_arduino_controller.py
#!/usr/bin/env python3
from email import header
from fileinput import filename
from constants import Mode, Constants
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

# TODO: stop measurement once PCE is below 50% of max
class SingleController:
    def __init__(
        self,
        COM: str,
        SERIAL_BAUD_RATE: int,
        trial_name: str,
        date: str,
        trial_dir: str,
        arduino_ids,
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
        self.run_finished = False
        self.arduino_ids = arduino_ids

        self.mode = ""
        self.scan_filename = ""
        self.file_path = ""
        self.mppt_compressed_file_path = ""

        self.HW_ID = 0
        self.arduinoID = Constants.unknown_Arduino_ID
        self.trial_name = trial_name
        self.today = date
        self.trial_dir = trial_dir
        self.start = time.time()

        self.scan_arr_width = 0
        self.mppt_arr_width = 0


    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            self.reset_arduino()
            # time.sleep(0.5)
            done = False
            while not done:
                with self.reading_lock:
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    if line:
                        custom_print(
                            f"Boot Stage Arduino {self.arduinoID} Output:", line
                        )
                    if "HW_ID" in line:
                        self.HW_ID = line.split(":")[-1]
                        if self.HW_ID in self.arduino_ids:
                            self.arduinoID = str(self.arduino_ids[self.HW_ID])
                    if "Arduino Ready" in line:
                        done = True
            self.ser.reset_input_buffer()

        except serial.SerialException as e:
            custom_print(f"Failed to connect to {self.port}. Error: {e}")
            return ()
        return (self.HW_ID, self.arduinoID)

    def disconnect(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None

    def reset_arduino(self):
        """
        Resets the specified Arduino by toggling the DTR signal.
        """
        try:
            if self.ser and self.ser.is_open:
                self.ser.setDTR(False)
                time.sleep(0.1)  # Wait for 100ms
                self.ser.setDTR(True)
                custom_print(f"Arduino has been reset.")
            else:
                custom_print(f"Arduino is not connected.")
        except Exception as e:
            custom_print(f"Failed to reset Arduino: {e}")

    def send_command(self):
        sent = False
        measurement_started = False
        line = ""
        while not sent:
            try:
                with self.write_lock:
                    self.ser.write(self.command.encode())  # send data to arduino
                    custom_print(f"Sent Scan Start Command {self.command}")
                    sent = True
            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                break

        while not measurement_started:
            try:
                with self.reading_lock:
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    custom_print(f"INIT STAGE ARDUINO {self.arduinoID} OUTPUT:", line)
                    if "Measurement Started" in line:
                        measurement_started = True
            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                break

    def scan(self, params):
        light_idx = Constants.params[Mode.SCAN].index(Constants.scan_mode_param)
        LIGHT_STATUS = int(params[light_idx])
        custom_print("Scan Initiated")

        if LIGHT_STATUS == 0:
            LIGHT_STATUS = "dark"
        else:
            LIGHT_STATUS = "light"

        file_name = (
            self.today
            + self.trial_name
            + "__"
            + f"ID{self.arduinoID}"
            + "__"
            + LIGHT_STATUS
            + "__"
            + "scan.csv"
        )
        self.file_path = os.path.join(self.trial_dir, file_name)
        self.mode = Mode.SCAN
        self.command = "scan," + ",".join(params) + ","
        custom_print(f"Starting scan with parameters: {self.command}")

        # Create header array
        voltage_lambda = lambda value: "Pixel_" + str(value + 1) + " V"
        amperage_lambda = lambda value: "Pixel_" + str(value + 1) + " mA"
        header_arr = ["Time", "Voltage_Applied"]
        header_arr.extend(
            [f(value) for value in range(8) for f in (voltage_lambda, amperage_lambda)]
        )
        header_arr.append("ARUDUINOID")
        self.scan_arr_width = len(header_arr)

        # Run measurement
        self.send_command()
        self._create_array(params, header_arr)
        self._save_data()
        self._read_data()

    def mppt(self, scan_file_name, params):
        file_name_base = (
            self.today
            + self.trial_name
            + "__"
            + f"ID{self.arduinoID}"
            + "__"
        )

        self.file_path = os.path.join(self.trial_dir, file_name_base+ "mppt.csv")
        self.mppt_compressed_file_path = os.path.join(self.trial_dir, file_name_base+ "compressedmppt.csv")

        self.scan_filename = scan_file_name
        self.mode = Mode.MPPT

        # if self.scan_filename:
        #     VMPP = self.find_vmpp(scan_file_name)
        #     custom_print(f"PC: VMPP-> {VMPP}")

        # VMPP = "0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6"
        # TODO: reimplement vmpp

        self.command = "mppt," + ",".join(params) + ","

        # Create header array
        voltage_lambda = lambda value: "Pixel_" + str(value + 1) + " V"
        amperage_lambda = lambda value: "Pixel_" + str(value + 1) + " mA"
        power_lambda = lambda y: "Pixel_" + str(y) + " PCE"
        header_arr = ["Time"]
        pce_header = []
        header_arr.extend(
            [f(value) for value in range(8) for f in (voltage_lambda, amperage_lambda)]
        )
        pce_header.extend([power_lambda(value) for value in range(8)])
        header_arr.extend(pce_header)
        header_arr.append("ARUDUINOID")
        self.mppt_arr_width = len(header_arr)

        # Run measurement
        custom_print(f"Starting MPPT with parameters:  {self.command}")
        self.send_command()
        self._create_array(params, header_arr)
        self._save_data()
        self._read_data()

    def _create_array(self, params, header_arr):
        num_params = len(params) + 2
        self.arr = np.empty([num_params, len(header_arr)], dtype="object")
        for idx, param in enumerate(params):
            self.arr[idx][0] = Constants.params[self.mode][idx]
            self.arr[idx][1] = param
        self.arr[num_params - 2][0] = "Start Date"
        self.arr[num_params - 2][1] = self.today
        self.arr[num_params - 1] = header_arr

    def _read_data(self):
        """
        - Reads data outputed on serial bus by arduino
        - Saves data after certain interval of time
        - Does not need to manage mode because that is taken care of on the arduino
        """
        done = False
        line = ""

        while self.should_run and not done:
            try:
                with self.reading_lock:
                    line = self.ser.readline().decode("unicode_escape").rstrip()
                    data_list = line.split(",")
                    if len(data_list) > 0:
                        # custom_print(data_list)

                        custom_print(f"ARDUINO{self.arduinoID}: {line}")

                        if len(data_list) > 13:
                            self.arr = np.append(
                                self.arr, np.array([data_list], dtype="object"), axis=0
                            )

                        if self.arr.shape[0] > Constants.line_per_save:
                            self._save_data()

                        # if self.mode == "PNO" and abs(time.time() - pno_time_org) > pno_time_save * 60:
                        #     self._gen_pno_graphs(str(os.path.abspath(self.file_name)), self.scan_filename)
                        #     pno_time_org = time.time()
                        if line == "Done!":
                            self._save_data()
                            self.ser.flush()
                            done = True

            except serial.SerialException as e:
                custom_print(f"Communication error on {self.port}. Error: {e}")
                self.run_finished = True
                break
        self.run_finished = True

    def _save_data(self) -> str:
        """
        - saves numpy array to csv file with the option to save at different time intervals
        - wipes self.arr to reduce memory usage

        Returns
        -------
        file_name
            file_name for file that was just saved
        """
        if not os.path.exists(self.file_path):
            np.savetxt(self.file_path, self.arr, delimiter=",", fmt="%s")
            if self.mode == Mode.SCAN:
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif self.mode == Mode.MPPT:
                np.savetxt(self.mppt_compressed_file_path, self.arr, delimiter=",", fmt="%s")
                self.arr = np.empty([1, self.mppt_arr_width], dtype="object")
        else:
            with open(self.file_path, "ab") as f:
                np.savetxt(f, self.arr[1:, :], delimiter=",", fmt="%s")
            if self.mode == Mode.SCAN:
                self.arr = np.empty([1, self.scan_arr_width], dtype="object")
            elif self.mode == Mode.MPPT:
                float_array = self.arr[1:, :].astype(float)
                result_array = np.nan_to_num(float_array, nan=0.0)
                avg_array = np.mean(result_array, axis=0)[np.newaxis,:]
                with open(self.mppt_compressed_file_path, "ab") as f:
                    np.savetxt(f, avg_array.astype(str), delimiter=",", fmt="%s")

                self.arr = np.empty([1, self.mppt_arr_width], dtype="object")

        custom_print(f"ARDUINO {self.arduinoID} SAVED DATA")

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
        self.file_path = (
            self.trial_dir
            + self.trial_name
            + self.today
            + light_status
            + "ID"
            + self.arduinoID
            + "constant_voltage.csv"
        )
        custom_print("constant voltage started")

        self.command = (
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

        custom_print(f"Parameters: {self.command}")
        self._start_scan(
            SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status
        )
        self._read_data()


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
