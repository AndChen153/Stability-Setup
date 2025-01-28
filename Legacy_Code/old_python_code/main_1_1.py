# from statistics import mode
import controller_1_2 as controller
import GUI_1_0
from data_visualization import data_show_1_0 as data_show
import math
import serial.tools.list_ports
import logging
log_name = 'main_1_1.py'


arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
]

if not arduino_ports:
    logging.error('%s No Arduino found', log_name)
    raise IOError()
elif len(arduino_ports) > 1:
    COM = "COM25"
    logging.info(f'Multiple Arduinos found, com port set manually to {COM}')
    arduino_controller = controller.stability_setup(COM, 115200)
else:
    # print("One Aruino found, using port:", arduino_ports[0])
    logging.info(f"One Aruino found, using port: {arduino_ports[0]}")
    arduino_controller = controller.stability_setup(arduino_ports[0], 115200)



gui = GUI_1_0.UserInterface()

# def scanMAP(object, inputs):
#     print("STARTED SCAN", object, inputs)
#     filename = object.scan(float(inputs[0]), float(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]))
#     print("DONE SCAN", object, inputs)
#     return filename

# def pnoMAP(object, inputs):
#     print("STARTED PNO", object, inputs)
#     filename = object.pno(float(inputs[0]), float(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]))
#     print("DONE PNO", object, inputs)
#     return filename


#TODO implement light status for PNO to throw error whenever light status turns off
if __name__ == '__main__':

    while True:
        params,mode = gui.open()

        if mode == "Scan":
            logging.info("Scan started with settings: ", float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            # print(params, "JV")
            scan_filename = arduino_controller.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            data_show.show_scan_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)
        elif mode == "PNO":
            logging.info("PNO started with settings: ", float(params[0]), float(params[1]), int(params[2]), int(params[3]))
            # print(params,)
            # time_per_block = 30 # minutes
            # NUMBLOCKS = int(int(params[4])/time_per_block)
            total_pno_files = []
            total_scan_files = []
            scan_filename = arduino_controller.scan(1.2, 0.03, 2, 50, 1)
            data_show.show_scan_graphs(scan_filename, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)
            pno_filename = arduino_controller.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]), scan_filename)

            # for i in range(NUMBLOCKS):
            #     scan_filename = arduino_controller.scan(1.2, 0.03, 2, 50, 1)
            #     pno_filename = arduino_controller.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), time_per_block, scan_filename)
            #     total_scan_files.append(scan_filename)
            #     total_pno_files.append(pno_filename)
            # for i in total_pno_files:
            #     data_show.show_pce_graphs(i)


