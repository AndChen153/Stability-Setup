from statistics import mode
import arduinoController1_1
import GUI
from dataVisualization import dataShow
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ac = arduinoController1_1.StabilitySetup("COM5", 115200)
ac = arduinoController1_1.StabilitySetup()
gui = GUI.UserInterface()


#TODO implement light status for PNO to throw error whenever light status turns off
#TODO measurment for 500/1000 hours
if __name__ == '__main__':
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
            dataShow.showJVGraphs(ac.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4])))
        elif mode == "PNO":
            print(params, "PNO")
            # dataShow.showPCEGraphs(arrPCE, graphNamePCE[-1])

            dataShow.showPCEGraphs(ac.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), 0)

