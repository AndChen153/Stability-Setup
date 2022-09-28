import arduinoController1_1
import GUI
import numpy as np
import matplotlib.pyplot as plt


# ac = arduinoController1_1.StabilitySetup("COM5", 115200)
ac = arduinoController1_1.StabilitySetup()
gui = GUI.UserInterface()



def showPnOPlot(arr):


if __name__ == '__main__':
    gui.open(ac)

    # darkArr = ac.scan(1.2, 0.03, 3, 100, 0)
    # x = input("press enter when light turned on")
    # lightArr = ac.scan(1.2, 0.03, 3, 100, 1)

