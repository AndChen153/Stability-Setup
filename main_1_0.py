from statistics import mode
import controller_1_1
import GUI_1_0
from dataVisualization import dataShow
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import serial.tools.list_ports
import multiprocessing


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


ac01 = controller_1_1.StabilitySetup(arduino_ports[0], 115200)
# ac23 = controller_1_1.StabilitySetup(arduino_ports[1], 115200)

# ac01 = controller1_1.StabilitySetup("COM23", 115200)
# ac23 = controller1_1.StabilitySetup("COM23", 115200)


# ac = arduinoController1_1.StabilitySetup()
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

    # filePathJV = r".\data\Sept 9 MPPT 8 Pixel test\scanlight_Sep-09-2022 11_14_58.csv"
    # filepathPCE = r".\data\Sept 9 MPPT 8 Pixel test\PnOSep-09-2022 11_22_45.csv"

    # arrJV = np.loadtxt(filePathJV, delimiter=",", dtype=str)
    # graphNameJV = filePathJV.split('\\')

    # arrPCE = np.loadtxt(filepathPCE, delimiter=",", dtype=str)
    # graphNamePCE = filepathPCE.split('\\')
    while True:
        params,mode = gui.open()

        if mode == "Scan":
            print(params, "JV")
            # dataShow.showJVGraphs(arrJV, graphNameJV[-1])
            fileName01 = ac01.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            # fileName23 = ac23.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            # pool = multiprocessing.Pool()
            # result = pool.map(scanMAP, ((ac01, params)))#, (ac23,params)))

            # print(result[0], result[1])
            dataShow.showJVGraphs(fileName01)
            # dataShow.showJVGraphs(result[1])
        elif mode == "PNO":
            print(params, "PNO")
            # dataShow.showPCEGraphs(arrPCE, graphNamePCE[-1])
            # fileName01 = ac01.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            # fileName23 = ac23.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))

            pool = multiprocessing.Pool()
            result = pool.map(pnoMAP, ((ac01, params), (ac23,params)))

            print(result[0], result[1])
            dataShow.showJVGraphs(result[0])
            dataShow.showJVGraphs(result[1])

