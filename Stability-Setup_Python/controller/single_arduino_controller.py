# single_arduino_controller.py
#!/usr/bin/env python3
from email import header
from fileinput import filename
from constants import Mode, Constants
from data_visualization import data_plotter
from helper.global_helpers import logger
import serial
import time
from datetime import datetime
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import threading
import copy
import logging

class SingleController:
    def __init__(
        self,
        COM: str,
        trial_name: str,
        trial_dir: str,
        arduino_ids,
    ) -> None:
        """
        Parameters
        ----------
        COM : str
            com port to communicate with arduino
            typically "COM5" or "COM3"
            serial rate to communicate with arduino
            set to 115200 in arduino code
        """
        self.port = COM
        self.ser = None
        self.reading_lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.should_run = True
        self.baud_rate = 115200
        self.run_finished = False
        self.arduino_ids = arduino_ids

        self.mode = ""
        self.scan_filepath = None
        self.file_path = ""
        self.mppt_compressed_file_path = ""

        self.HW_ID = 0
        self.arduinoID = Constants.unknown_Arduino_ID
        self.trial_name = trial_name
        self.date = None
        self.trial_dir = trial_dir
        self.start = time.time()

        self.scan_arr_width = 0
        self.mppt_arr_width = 0

    def connect(self):
        failed_connect = False
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
                        logger.log(
                            f"Boot Stage Arduino {self.arduinoID} Output:", line
                        )
                    if "HW_ID" in line:
                        self.HW_ID = line.split(":")[-1]
                        if self.HW_ID in self.arduino_ids:
                            self.arduinoID = str(self.arduino_ids[self.HW_ID])
                    elif "Arduino Ready" in line:
                        done = True
                    elif "Sensor Initialization Failed." in line:
                        done = True
                        failed_connect = True
            self.ser.reset_input_buffer()

        except serial.SerialException as e:
            logger.log(f"Failed to connect to {self.port}. Error: {e}")
            return ()
        if failed_connect:
            logger.log(f"Arduino Connection to {self.arduinoID} Failed. Disconnecting...")
            self.disconnect()
            return ()
        else:
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
                logger.log(f"Arduino has been reset.")
            else:
                logger.log(f"Arduino is not connected.")
        except Exception as e:
            logger.log(f"Failed to reset Arduino: {e}")

    def _send_command(self, mode, params:dict[str, str]):
        measurement_started = False
        # Create commands array to send to arduino one by one
        # This is for easier management and less variables on arduino side
        # add "\n" to indicate end of command
        commands = [Constants.arduino_commands[mode] + ',null\n']
        # translate param names to correct ID for arduino to understand
        translation_dict = Constants.translation_dict[mode]
        for key in params:
            if key not in translation_dict:
                continue
            translated_key = str(translation_dict[key])
            if key == Constants.mppt_voltage_range_param:
                vset_arr = ",".join(params[key])
                commands.append(translated_key + "," + vset_arr + '\n')
            else:
                commands.append(translated_key + "," + str(params[key]) + '\n')
        commands.append("done \n")
        line = ""
        logger.log("Sending Commands to Arduino: ", commands)
        while commands:
            try:
                with self.write_lock:
                    command = commands.pop(0)
                    self.ser.write(command.encode())  # send data to arduino
                    # logger.log(f"Sent to Arduino: {command}")
                    time.sleep(0.1)
            except serial.SerialException as e:
                logger.log(f"Communication error on {self.port}. Error: {e}")
                break

        while not measurement_started:
            try:
                with self.reading_lock:
                    line = self.ser.readline().decode().strip()
                    # line = self.ser.readline().decode('unicode_escape').rstrip()
                    logger.log(f"INIT STAGE ARDUINO {self.arduinoID} OUTPUT:", line)
                    if "Measurement Started" in line:
                        measurement_started = True
            except serial.SerialException as e:
                logger.log(f"Communication error on {self.port}. Error: {e}")
                break

    def scan(self, params: dict[str, str]):
        logger.log("Scan Initiated")

        LIGHT_STATUS = params[Constants.scan_mode_param]
        if LIGHT_STATUS == 0:
            LIGHT_STATUS = "dark"
        else:
            LIGHT_STATUS = "light"

        file_name = (
            self.date
            + self.trial_name
            + "__"
            + f"ID{self.arduinoID}"
            + "__"
            + LIGHT_STATUS
            + "__"
            + "scan.csv"
        )

        self.file_path = os.path.join(self.trial_dir, file_name)
        self.scan_filepath = self.file_path
        self.mode = Mode.SCAN
        logger.log(f"Starting scan with parameters: {params}")

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
        self._send_command(Mode.SCAN, params)
        self._create_array(params, header_arr)
        self._save_data()
        self._read_data()

    def mppt(self, params: dict[str, str]):
        file_name_base = (
            self.date
            + self.trial_name
            + "__"
            + f"ID{self.arduinoID}"
            + "__"
        )

        multiplier = float(params["Starting Voltage Multiplier (%)"])

        self.file_path = os.path.join(self.trial_dir, file_name_base+ "mppt.csv")
        self.mppt_compressed_file_path = os.path.join(self.trial_dir, file_name_base+ "compressedmppt.csv")

        self.mode = Mode.MPPT
        copied_params = copy.deepcopy(params)
        entered_V = copied_params[Constants.mppt_voltage_range_param]
        if self.scan_filepath:
            try:
                starting_V = self.find_starting_voltage(self.scan_filepath, multiplier)
                starting_V = [str(val) for val in starting_V]
            except:
                starting_V = [entered_V for i in range(8)]
        else:
            starting_V = [entered_V for i in range(8)]

        copied_params[Constants.mppt_voltage_range_param] = starting_V

        # Create header array
        voltage_lambda = lambda value: "Pixel_" + str(value + 1) + " V"
        amperage_lambda = lambda value: "Pixel_" + str(value + 1) + " mA"
        header_arr = ["Time"]
        header_arr.extend(
            [f(value) for value in range(8) for f in (voltage_lambda, amperage_lambda)]
        )
        header_arr.append("ARUDUINOID")
        self.mppt_arr_width = len(header_arr)

        # Run measurement
        logger.log(f"Starting MPPT with parameters:  {copied_params}")
        self._send_command(Mode.MPPT, copied_params)
        self._create_array(copied_params, header_arr)
        self._save_data()
        self._read_data()

    def _create_array(self, params, header_arr):
        num_params = len(params) + 2
        self.arr = np.empty([num_params, len(header_arr)], dtype="object")
        for idx, key in enumerate(params):
            self.arr[idx][0] = key

            if isinstance(params[key], (list, np.ndarray)):
                value_to_store = " ".join(params[key])
            else:
                value_to_store = params[key]
            self.arr[idx][1] = value_to_store

        self.arr[num_params - 2][0] = "Start Date"
        self.arr[num_params - 2][1] = self.date
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
                        # logger.log(data_list)

                        logger.log(f"ARDUINO{self.arduinoID}: {line}")

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
                logger.log(f"Communication error on {self.port}. Error: {e}")
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

        logger.log(f"ARDUINO {self.arduinoID} SAVED DATA")

    def find_vmpp(self, scan_file_name):
        arr = np.loadtxt(scan_file_name, delimiter=",", dtype=str)
        scan_file_name = scan_file_name.split("\\")
        # logger.log(arr)
        headers = arr[6, :]
        headerDict = {value: index for index, value in enumerate(headers)}
        # logger.log(headerDict)
        arr = arr[7:, :]
        length = len(headers) - 1
        # logger.log(length)

        jv_list = []

        for i in range(2, length):
            jv_list.append(arr[:, i])

        j_list = []  # current
        v_list = []  # voltage
        for i in range(0, len(jv_list), 2):
            # logger.log(i)
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

    def find_starting_voltage(self, scan_filename, multiplier):
        arr = np.loadtxt(scan_filename, delimiter=",", dtype=str)
        header_row = np.where(arr == "Time")[0][0]

        meta_data = {}
        for data in arr[:header_row, :2]:
            meta_data[data[0]] = data[1]

        arr = arr[header_row + 1 :, :]

        data = arr[:, 2:-1]

        pixel_V = data[:, ::2][:, ::-1].astype(float)
        pixel_mA = data[:, 1::2][:, ::-1].astype(float)
        voc = []
        for pixel_idx in range(8):
            voc_idx = min(
                    range(len(pixel_mA[:, pixel_idx])),
                    key=lambda x: abs(pixel_mA[:, pixel_idx][x]),
                )
            starting_V = multiplier*float(pixel_V[voc_idx, pixel_idx])
            starting_V = round(starting_V, 2)
            voc.append(starting_V)

        return voc

    def printTime(self):
        end = time.time()
        total_time = end - self.start
        logger.log("\n" + str(total_time))

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
            + self.date
            + light_status
            + "ID"
            + self.arduinoID
            + "constant_voltage.csv"
        )
        logger.log("constant voltage started")

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

        logger.log(f"Parameters: {self.command}")
        self._start_scan(
            SCAN_RANGE, SCAN_STEP_SIZE, SCAN_READ_COUNT, SCAN_RATE, light_status
        )
        self._read_data()