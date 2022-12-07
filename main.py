from statistics import mode
import controller1_1
import GUI
from dataVisualization import dataShow
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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


ac = controller1_1.StabilitySetup(arduino_ports[0], 115200)
# ac = arduinoController1_1.StabilitySetup()
gui = GUI.UserInterface()


#TODO implement light status for PNO to throw error whenever light status turns off
#TODO measurment for 500/1000 hours
if __name__ == '__main__':
    # dataShow.showJVGraphs(arr, fileName)
    # filePathJVTest = r".\data\scandarkOct-31-2022 15_50_07.csv"

    filePathJV = r".\data\Sept 9 MPPT 8 Pixel test\scanlight_Sep-09-2022 11_14_58.csv"
    filepathPCE = r".\data\Sept 9 MPPT 8 Pixel test\PnOSep-09-2022 11_22_45.csv"

    arrJV = np.loadtxt(filePathJV, delimiter=",", dtype=str)
    graphNameJV = filePathJV.split('\\')

    arrPCE = np.loadtxt(filepathPCE, delimiter=",", dtype=str)
    graphNamePCE = filepathPCE.split('\\')

    # dataShow.showJVGraphs(arrJV, graphNameJV[-1])
    # dataShow.showPCEGraphs(arrPCE, graphNamePCE[-1])

    while True:
        params,mode = gui.open(ac)

        if mode == "Scan":
            print(params, "JV")
            # dataShow.showJVGraphs(arrJV, graphNameJV[-1])
            arr, fileName = ac.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            print(fileName)
            dataShow.showJVGraphs(fileName)
        elif mode == "PNO":
            print(params, "PNO")
            # dataShow.showPCEGraphs(arrPCE, graphNamePCE[-1])
            arr, fileName = ac.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4]))
            print(fileName)
            dataShow.showPCEGraphs(fileName)

