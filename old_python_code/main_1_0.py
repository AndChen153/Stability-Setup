# from statistics import mode
import python_code.controller_1_1 as controller_1_1
import GUI_1_0
from data_visualization import dataShow_1_0
import math
import serial.tools.list_ports


arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
]

if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    print('Multiple Arduinos found - using the first')
    
print(arduino_ports[0])


# arduino_controller = controller_1_1.stability_setup(arduino_ports[0], 115200)
arduino_controller = controller_1_1.stability_setup("COM25", 115200)


gui = GUI_1_0.UserInterface()

#TODO implement light status for PNO to throw error whenever light status turns off
if __name__ == '__main__':

    while True:
        params,mode = gui.open()

        if mode == "Scan":
            print(params, "JV")
            fileName = arduino_controller.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            dataShow_1_0.show_jv_graphs(fileName)
        elif mode == "PNO":
            print(params, "PNO")
            fileName = arduino_controller.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))

            dataShow_1_0.show_pce_graphs(fileName)

