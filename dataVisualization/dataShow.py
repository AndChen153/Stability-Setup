#%%
import matplotlib.pyplot as plt
import numpy as np


def showPCEGraphs(arr, graphName):
    headers = arr[4,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    arr = arr[5:, :]


    time = arr[:,headerDict["Time"]]
    pceList = []

    for i in range(headerDict["Pixel 0 PCE"], (headerDict["Pixel 7 PCE"]+1)):
        pceList.append(arr[:,i])

    time = [float(i) for i in time]
    for i in range(len(pceList)):
        pceList[i] = [float(j) for j in pceList[i]]


    for i in range(len(pceList)):
        lineName = "PCE" + str(i)
        plt.plot(time,pceList[i], label = lineName)

    plt.xlim(0,120)
    plt.ylim(0,15)
    plt.title(graphName[:-4])
    plt.xlabel('Time [s]')
    plt.ylabel('PCE [%]')
    plt.legend(bbox_to_anchor = (1.2, 0.75))
    plt.show()

def showJVGraphs(arr, graphName):
    headers = arr[4,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[5:, :]


    jvList = []

    for i in range(headerDict["Pixel 0 V"], (headerDict["Pixel 7 mA"]+1)):
        jvList.append(arr[:,i])

    for i in range(0,len(jvList),2):
        jvList[i] = [float(j) for j in jvList[i]]

        jvList[i+1] = [float(x) / 0.128 for x in jvList[i+1]]

    ax = plt.gca()
    ax.spines['bottom'].set_position('zero')


    for i in range(0,len(jvList),2):
        lineName = "Pixel " + str(int(i/2))
        plt.plot(jvList[i],jvList[i+1], label = lineName)

    plt.xlim(0,1.4)
    plt.ylim(-40, 30)
    plt.title(graphName[:-4])
    plt.xlabel('Bias [V]')
    plt.ylabel('Jmeas [mA/cm]')
    plt.legend(bbox_to_anchor = (1.24, 0.75))
    plt.show()

if __name__ == '__main__':
    filepathPCE = r"..\data\Sept 9 MPPT 8 Pixel test\PnOSep-09-2022 11_22_45.csv"
    filePathJV = r"..\data\Sept 9 MPPT 8 Pixel test\scanlight_Sep-09-2022 11_14_58.csv"
    arrPCE = np.loadtxt(filepathPCE, delimiter=",", dtype=str)
    graphNamePCE = filepathPCE.split('\\')

    arrJV = np.loadtxt(filePathJV, delimiter=",", dtype=str)
    graphNameJV = filePathJV.split('\\')
    showPCEGraphs(arrPCE, graphNamePCE[-1])
    showJVGraphs(arrJV, graphNameJV[-1])


# %%
