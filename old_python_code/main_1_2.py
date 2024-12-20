# from statistics import mode
from src_python import controller_1_3 as arduino_controller
from src_python import GUI_1_0 as GUI
from src_python import arduino_assignment_1_0 as arduino_ports
from data_visualization import data_show_1_0 as data_show
from datetime import datetime
import threading

import logging
log_name = "main"
logging.basicConfig(filename='example.log',format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)

# def _multithreaded_scan(controller, params, scan_arr):
#     scan_filename = controller.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
#     scan_arr.append(scan_filename)
# def _multithreaded_pno(controller, params):
#     scan_filename = controller.scan(1.2, 0.03, 2, 50, 1)
#     data_show.show_jv_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)
#     pno_filename = controller.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]), scan_filename)
#     data_show.show_pce_graphs(pno_filename, scan_filename, show_dead_pixels = True)

def multithreaded_scan_wrapper(arduino, folder_path, today, params, scan_arr):
    communicator = arduino_controller.stability_setup(arduino["serial"], arduino["com"], 115200, folder_path, today)
    if communicator.connect():
        communicator.multithreaded_scan(params, scan_arr)

def multithreaded_pno_wrapper(arduino, folder_path, today, params, pno_arr, scan_file_name):
    communicator = arduino_controller.stability_setup(arduino["serial"], arduino["com"], 115200, folder_path, today)
    if communicator.connect():
        communicator.multithreaded_pno(scan_file_name, params, pno_arr)

def main():
    gui = GUI.UserInterface()

    today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
    folder_path = "./data/" + today + "/"
    threads = []


    while True:
        params,mode = gui.open()
        if mode == "Scan":
            all_scans = []
            for arduino in arduino_ports.get_arduino_assignments():
                t = threading.Thread(target = multithreaded_scan_wrapper, args=(arduino, folder_path, today, params, all_scans))
                t.start()
                threads.append(t)

            try:
                # Wait for all threads to complete
                for t in threads:
                    t.join()

                threads = []
            except KeyboardInterrupt:
                # On keyboard interrupt, signal all threads to stop and close their serial connections
                for communicator in threads:
                    communicator.stop()
                print("Stopped all threads and closed connections.")


            for scan_filename in all_scans:
                data_show.show_scan_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)

        elif mode == "PNO":
            all_scans = ["",""]
            all_pno = []
            # scan_params = (1.2, 0.03, 2, 50, 1)
            # for arduino in arduino_ports.get_arduino_assignments():
            #     t = threading.Thread(target = multithreaded_scan_wrapper, args=(arduino, folder_path, today, scan_params, all_scans))
            #     t.start()
            #     threads.append(t)

            # try:
            #     # Wait for all threads to complete
            #     for t in threads:
            #         t.join()

            #     threads = []
            # except KeyboardInterrupt:
            #     # On keyboard interrupt, signal all threads to stop and close their serial connections
            #     for communicator in threads:
            #         communicator.stop()
            #     print("Stopped all threads and closed connections.")

            # for scan_filename in all_scans:
            #     data_show.show_scan_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)

            for arduino,scan_filename in zip(arduino_ports.get_arduino_assignments(), all_scans):
                t = threading.Thread(target = multithreaded_pno_wrapper, args=(arduino, folder_path, today, params, all_pno, scan_filename))
                t.start()
                threads.append(t)

            try:
                # Wait for all threads to complete
                for t in threads:
                    t.join()

                threads = []
            except KeyboardInterrupt:
                # On keyboard interrupt, signal all threads to stop and close their serial connections
                for communicator in threads:
                    communicator.stop()
                print("Stopped all threads and closed connections.")

            for pno_filename in all_pno:
                data_show.show_pce_graphs(pno_filename)


#TODO implement light status for PNO to throw error whenever light status turns off
if __name__ == '__main__':
    main()