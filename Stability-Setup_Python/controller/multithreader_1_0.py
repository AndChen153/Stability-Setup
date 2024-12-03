from controller import single_arduino_controller_1_3 as single_arduino
from controller import arduino_assignment_1_0 as arduino_ports
from constants_1_0 import Mode, constants_controller
import threading

import logging
log_name = "main"
# logging.basicConfig(filename='example.log',format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)
class controller:
    def __init__(self, folder_path: str, today:str):
        self.folder_path = folder_path
        self.today = today
        self.threads = []
        self.arduino_assignments = arduino_ports.get_arduino_assignments()
        self.controllers = {}

        for arduino in self.arduino_assignments:
            ID = arduino["ID"]
            COM = arduino["com"]
            self.controllers[ID] = single_arduino.controller(arduinoID = ID,
                                                        COM = COM,
                                                        SERIAL_BAUD_RATE = constants_controller["serial_baud_rate"],
                                                        folder_path = self.folder_path,
                                                        today = self.today)
    def multithreaded_scan_wrapper(self, controller, params, scan_arr):
        if controller.connect():
            controller.multithreaded_scan(params, scan_arr)

    def multithreaded_constant_voltage_wrapper(self, controller, params, scan_arr):
        if controller.connect():
            controller.multithreaded_constant_voltage(params, scan_arr)

    def multithreaded_pno_wrapper(self, controller, params, pno_arr, scan_file_name):
        if controller.connect():
            controller.multithreaded_pno(scan_file_name, params, pno_arr)

    def run(self, mode, params):
        if mode == Mode.SCAN:
            all_scans = []

            for controller in self.controllers.keys():
                t = threading.Thread(target = self.multithreaded_scan_wrapper,
                                     args=(self.controllers[controller], params, all_scans))
                t.start()
                self.threads.append(t)

            try:
                # Wait for all threads to complete
                for t in self.threads:
                    t.join()
                self.threads = []
            except KeyboardInterrupt:
                # On keyboard interrupt, signal all threads to stop and close their serial connections
                for t in self.threads:
                    t.stop()
                print("Stopped all threads and closed connections.")

            return all_scans

        elif mode == Mode.PNO:
            all_scans = ["" for _ in self.arduino_assignments]
            all_pno = []
            # scan_params = (1.2, 0.03, 2, 50, 1)
            # for arduino in arduino_ports.get_arduino_assignments():
            #     t = threading.Thread(target = multithreaded_scan_wrapper, args=(arduino, folder_path, today, scan_params, all_scans))
            #     t.start()
            #     self.threads.append(t)

            # try:
            #     # Wait for all threads to complete
            #     for t in self.threads:
            #         t.join()

            #     self.threads = []
            # except KeyboardInterrupt:
            #     # On keyboard interrupt, signal all threads to stop and close their serial connections
            #     for t in self.threads:
            #         t.stop()
            #     print("Stopped all threads and closed connections.")

            # for scan_filename in all_scans:
            #     data_show.show_scan_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)

            print(self.arduino_assignments)
            for controller,scan_filename in zip(self.controllers.keys(), all_scans):
                t = threading.Thread(target = self.multithreaded_pno_wrapper,
                                     args=(self.controllers[controller], params, all_pno, scan_filename))
                t.start()
                self.threads.append(t)

            try:
                # Wait for all threads to complete
                for t in self.threads:
                    t.join()
                self.threads = []
            except KeyboardInterrupt:
                # On keyboard interrupt, signal all threads to stop and close their serial connections
                for t in self.threads:
                    t.stop()
                print("Stopped all threads and closed connections.")

            return all_pno


        elif mode == Mode.CONSTANT:
            all_scans = []
            print("arduino assignments: ", self.arduino_assignments)
            for controller in self.controllers.keys():
                t = threading.Thread(target = self.multithreaded_constant_voltage_wrapper,
                                     args=(self.controllers[controller], params, all_scans))
                t.start()
                self.threads.append(t)

            try:
                # Wait for all threads to complete
                for t in self.threads:
                    t.join()
                self.threads = []
            except KeyboardInterrupt:
                # On keyboard interrupt, signal all threads to stop and close their serial connections
                for t in self.threads:
                    t.stop()
                print("Stopped all threads and closed connections.")