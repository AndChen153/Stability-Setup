# from statistics import mode
import pythonCode.controller_1_1 as controller_1_1
import GUI_1_0
from dataVisualization import dataShow
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


# arduinoController = controller_1_1.StabilitySetup(arduino_ports[0], 115200)
arduinoController = controller_1_1.StabilitySetup("COM25", 115200)


gui = GUI_1_0.UserInterface()

def scanMAP(object, inputs):
    print("STARTED SCAN", object, inputs)
    fileName = object.scan(float(inputs[0]), float(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]))
    print("DONE SCAN", object, inputs)
    return fileName

def pnoMAP(object, inputs):
    print("STARTED PNO", object, inputs)
    fileName = object.pno(float(inputs[0]), float(inputs[1]), int(inputs[2]), int(inputs[3]), int(inputs[4]))
    print("DONE PNO", object, inputs)
    return fileName


#TODO implement light status for PNO to throw error whenever light status turns off
if __name__ == '__main__':

    while True:
        params,mode = gui.open()

        if mode == "Scan":
            print(params, "JV")
            fileName = arduinoController.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            dataShow.showJVGraphs(fileName)
        elif mode == "PNO":
            print(params, "PNO")
            fileName = arduinoController.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))

            dataShow.showPCEGraphs(fileName)

