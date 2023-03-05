import PySimpleGUI as sg
from controller_1_1 import StabilitySetup

# Create an event loop


class UserInterface:
    def __init__(self) -> None:
        pass

    # defaults
    # [sg.Text('SCAN_RANGE (V):'), sg.InputText("1.2")],
    # [sg.Text('SCAN_STEP_SIZE (V):'), sg.InputText("0.03")],
    # [sg.Text('SCAN_READ_COUNT:'), sg.InputText("3")],
    # [sg.Text('SCAN_RATE (mV/s):'), sg.InputText("50")],
    # [sg.Text('SCAN_MODE (0 = dark, 1 = light):'), sg.InputText("1")],
    def make_win1(self):
        layoutScan = [ [sg.Button("Scan"), sg.Button("PNO"), sg.Button("GO")],
                            [sg.Text('SCAN_RANGE (V):'), sg.InputText("1.2")],
                            [sg.Text('SCAN_STEP_SIZE (V):'), sg.InputText("0.03")],
                            [sg.Text('SCAN_READ_COUNT:'), sg.InputText("3")],
                            [sg.Text('SCAN_RATE (mV/s):'), sg.InputText("50")],
                            [sg.Text('SCAN_MODE (0 = dark, 1 = light):'), sg.InputText("1")],

                            ]
        return sg.Window('Scan', layoutScan, finalize=True)


    # defaults
    # [sg.Button("Scan"), sg.Button("PNO"), sg.Button("GO")],
    # [sg.Text('PNO_STARTING_VOLTAGE (V):'), sg.InputText("0.09")],
    # [sg.Text('PNO_STEP_SIZE (V):'), sg.InputText("0.02")],
    # [sg.Text('PNO_MEASUREMENTS_PER_STEP:'), sg.InputText("5")],
    # [sg.Text('PNO_MEASUREMENT_DELAY (mV/s):'), sg.InputText("100")],
    # [sg.Text('Time (mins):'), sg.InputText("120")]
    def make_win2(self):
        layoutPnO = [  [sg.Button("Scan"), sg.Button("PNO"), sg.Button("GO")],
                            [sg.Text('PNO_STARTING_VOLTAGE (V):'), sg.InputText("0.90")],
                            [sg.Text('PNO_STEP_SIZE (V):'), sg.InputText("0.05")],
                            [sg.Text('PNO_MEASUREMENTS_PER_STEP:'), sg.InputText("5")],
                            [sg.Text('PNO_MEASUREMENT_DELAY (ms):'), sg.InputText("50")],
                            [sg.Text('Time (hours):'), sg.InputText("120")]
                            ]
        return sg.Window('PNO', layoutPnO, finalize=True)

    def make_win3(self):
        layoutLight = [[sg.Text('Press When Light is On')],
                       [sg.Button("Continue")],
                            ]
        return sg.Window('Light', layoutLight, finalize=True)

    def open(self):
        window1, window2, window3 = self.make_win1(), None, None
        mode = "Scan"

        # while True:
        #     event, values = self.window.read()

        #     if event == "Scan":
        #         print("runscan")
        #         self.window.close()
        #         self.window = sg.Window("StabilitySetup", self.layoutScan)
        #     elif event == "PNO":
        #         print("pnoset")
        #         self.window.close()
        #         self.window = sg.Window("StabilitySetup", self.layoutPnO)
        #     elif event == "GO":
        #         print("RUN")
        #     elif event == sg.WIN_CLOSED:
        #         break

        while True:             # Event Loop
            window, event, values = sg.read_all_windows()
            lightON = False

            if event == sg.WIN_CLOSED:
                break
            elif event == "PNO" and not window2:
                mode = "PNO"
                window2 = self.make_win2()
                if window1:
                    window1.close()
                    window1 = None

            elif event == "Scan" and not window1:
                mode = "Scan"
                window1 = self.make_win1()
                if window2:
                    window2.close()
                    window2 = None

            elif event == "GO":
                valueList = list(values.values())
                if mode == "Scan" and not window2:
                    if (int(valueList[-1]) == 1):
                        try:
                            window1.close()
                        except:
                            pass
                        try:
                            window2.close()
                        except:
                            pass
                        window3 = self.make_win3()
                    else:
                        try:
                            window1.close()
                        except:
                            pass
                        try:
                            window2.close()
                        except:
                            pass
                        return(valueList,mode)
                if mode == "PNO" and not window1:
                    try:
                        window1.close()
                    except:
                        pass
                    try:
                        window2.close()
                    except:
                        pass
                    window3 = self.make_win3()

            elif event == "Continue":
                try:
                    window3.close()
                except:
                    pass
                return(valueList,mode)
        try:
            window1.close()
        except:
            pass
        try:
            window2.close()
        except:
            pass
        try:
            window3.close()
        except:
            pass
