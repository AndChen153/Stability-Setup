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
if __name__ == '__main__':
    while True:
        params,mode = gui.open(ac)

        if mode == "Scan":
            print(params, "JV")
            # dataShow.showJVGraphs(ac.scan(float(params[0]), float(params[1]), int(params[2]), int(params[3]), int(params[4])))
        elif mode == "PNO":
            print(params, "PNO")
            # dataShow.showPCEGraphs(ac.pno(float(params[0]), float(params[1]), int(params[2]), int(params[3]), 0)

