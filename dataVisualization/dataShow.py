#%%
import matplotlib.pyplot as plt
import numpy as np
import numpy_indexed as npi
from labellines import labelLines

import sys
np.set_printoptions(threshold=sys.maxsize)



def showPCEGraphs(graphName, startingPoint = 0, pixels = None, divFactor = 50):
    # num_rows = 0
    # numCols = 0
    # for line in open(graphName):
    #     num_rows += 1
    #     numCols = len(np.array(line.split(",")))
    # arr = np.empty([num_rows,numCols])
    # arr = arr.astype("str")
    # row = 0
    # for line in open(graphName):
    #     arr[row] = np.array(line.split(","))
    #     row += 1

    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    graphName = graphName.split('\\')
    headers = arr[5,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    arr = arr[6:, :]


    time = arr[:,headerDict["Time"]]
    pceList = np.array(arr)
    average = pceList.shape[0]/divFactor
    # print(average)
    # print(range(headerDict["Pixel 0 PCE"], (headerDict["Pixel 7 PCE"]+1)))
    # pceList = np.delete(pceList, [1:headerDict["Pixel 0 PCE"]-1], 1)

    # UNCOMMENT LINE IF CSV INCLUDES VOLTAGE AND CURRENT
    pceList = np.delete(pceList, slice(1,65), axis=1)
    pceList = pceList[:,0:-1]
    for i in range(len(pceList)):
        pceList[i] = [float(j) if j != " ovf" else 0.0 for j in pceList[i]]
        pceList[i] = [float(j) if j != "nan" else 0.0 for j in pceList[i]]
        # # print(pceList[i])
        # pceList[i] = [float(30) if float(j) > 30 else j for j in pceList[i]]
    pceList = pceList.astype(float)
    # print(pceList)

    pceList[:,0] = np.floor(pceList[:,0]/average)
    time = np.unique(pceList[:,0])
    data = []
    # print(len(time))


    # print(len(npi.group_by(pceList[:, 0]).split(pceList[:, 8])))
    for i in range(1,pceList.shape[1]):
        avg = []
        colSplit = npi.group_by(pceList[:, 0]).split(pceList[:, i])
        for i in colSplit:
            avg.append(np.average(i))
        data.append(avg)
    time = np.array(time)
    data = np.array(data).T
    time*=average
    time/=3600

    # a = a[a[:, 0].argsort()])

    maxTime = max(time)*1.01
    maxPCE = 35
    print("MAXTIME", maxTime)
    print("MAXPCE", maxPCE)



    plt.figure(figsize=(10, 8))
    plt.xlim(0,maxTime)

    plt.ylim(bottom = -0, top = maxPCE)
    plt.title(graphName[-1][:-4])
    plt.xlabel('Time [hrs]')
    plt.ylabel('PCE [%]')
    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

    if pixels == None:
        for i in range(data.shape[1]):
            lineName = "PCE" + str(i)
            # print(np.array(pceList[i]))
            plt.plot(time,data[:,i], label = lineName)
    else:
        for i in pixels:
            lineName = "PCE" + str(i)
            # print(np.array(pceList[i]))
            plt.plot(time,data[:,i], label = lineName)

    labelLines(plt.gca().get_lines(), zorder=2.5)
    plt.legend(bbox_to_anchor=(1.15, 0.65))
    plt.show()

def showJVGraphsSmoothed(graphName, pixels = None):
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    graphName = graphName.split('\\')
    # print(arr)
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[6:, :]
    length = (len(headers) - 1)
    # print(length)

    jvList = []

    for i in range(2, length):
        jvList.append(arr[:,i])


    maxX = 0
    minX = 0
    maxY = 0
    minY = 0

    for i in range(0,len(jvList),2):
        # print(i)
        jvList[i] = [float(j) for j in jvList[i]]
        jvList[i+1] = [float(x) for x in jvList[i+1]]
        # jvList[i+1] = [float(x) / 0.128 for x in jvList[i+1]]

        if max(jvList[i]) > maxX: maxX = max(jvList[i])
        if min(jvList[i]) < minX: minX = min(jvList[i])
        if max(jvList[i+1]) > maxY: maxY = max(jvList[i+1])
        if min(jvList[i+1]) < minY: minY = min(jvList[i+1])


    maxX *= 1.1
    minX *= 1.1
    maxY *= 1.1
    minY *= 1.1



    # data = []
    # jvList = np.array(jvList)
    # for i in range(1,jvList.shape[1]):
    #     avg = []
    #     colSplit = npi.group_by(jvList[:, 0]).split(jvList[:, i])
    #     for i in colSplit:
    #         avg.append(np.average(i))
    #     data.append(avg)
    jvList = np.array(jvList).T
    data = jvList

    print(jvList.shape)
    # print(len(npi.group_by(pceList[:, 0]).split(pceList[:, 8])))
    for i in range(0,jvList.shape[1],2):
        # print(jvList[:, i+1])

        # print(kalmanFilter(jvList[:, i+1]))
        jvList[:, i+1] = kalmanFilter(jvList[:, i+1])
        # break
    # print(np.array(data).T.shape)
    jvList = np.array(data).T

    plt.figure(figsize=(10, 8))
    plt.xlim(minX,maxX)
    plt.ylim(minY, maxY)
    plt.title(graphName[-1][:-4])
    plt.xlabel('Bias [V]')
    plt.ylabel('Current [mA]')
    # plt.ylabel('Jmeas [mA/cm]')
    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)


    if pixels == None:
        for i in range(0,len(jvList),2):
            # print(i)
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)
    else:
        for i in pixels:
            # print(i)
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

    ax = plt.gca()
    ax.spines['bottom'].set_position('zero')
    labelLines(plt.gca().get_lines(), zorder=2.5)

    plt.legend(bbox_to_anchor=(1.18, 0.7))

    plt.show()

def showJVGraphs(graphName, pixels = None):
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    graphName = graphName.split('\\')
    # print(arr)
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[6:, :]
    length = (len(headers) - 1)
    # print(length)

    jvList = []

    for i in range(2, length):
        jvList.append(arr[:,i])


    maxX = 0
    minX = 0
    maxY = 0
    minY = 0

    for i in range(0,len(jvList),2):
        # print(i)
        jvList[i] = [float(j) for j in jvList[i]]
        jvList[i+1] = [float(x) for x in jvList[i+1]]
        # jvList[i+1] = [float(x) / 0.128 for x in jvList[i+1]]

        if max(jvList[i]) > maxX: maxX = max(jvList[i])
        if min(jvList[i]) < minX: minX = min(jvList[i])
        if max(jvList[i+1]) > maxY: maxY = max(jvList[i+1])
        if min(jvList[i+1]) < minY: minY = min(jvList[i+1])


    maxX *= 1.1
    minX *= 1.1
    maxY *= 1.1
    minY *= 1.1



    # data = []
    # jvList = np.array(jvList)
    # for i in range(1,jvList.shape[1]):
    #     avg = []
    #     colSplit = npi.group_by(jvList[:, 0]).split(jvList[:, i])
    #     for i in colSplit:
    #         avg.append(np.average(i))
    #     data.append(avg)

    plt.figure(figsize=(10, 8))
    plt.xlim(minX,maxX)
    plt.ylim(minY, maxY)
    plt.title(graphName[-1][:-4])
    plt.xlabel('Bias [V]')
    plt.ylabel('Current [mA]')
    # plt.ylabel('Jmeas [mA/cm]')
    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

    if pixels == None:
        for i in range(0,len(jvList),2):
            # print(i)
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)
    else:
        for i in pixels:
            # print(i)
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

    ax = plt.gca()
    ax.spines['bottom'].set_position('zero')
    labelLines(plt.gca().get_lines(), zorder=2.5)

    plt.legend(bbox_to_anchor=(1.18, 0.7))

    plt.show()

def kalmanFilter(predictions: np.ndarray, process_noise = 1e-1, measurement_var = 0.1) -> np.ndarray:
        '''
        Inputs:
            - Context predictions (e.g. slope, walking speed, etc.)
            - Process noise for predictions
            - Measurement uncertainty (in the form of variance)
        Output:
            - Updated estimates of context
        '''

        estimates = []

        # Initialize
        prior_estimate = predictions[0]
        prior_var = 0.1

        for i in range(len(predictions)):

            slope_measurement = np.float64(predictions[i])

            # Update
            kalman_gain = prior_var / (prior_var + measurement_var) # Kn
            estimate = prior_estimate + kalman_gain*(slope_measurement-prior_estimate) # Xnn
            estimates.append(estimate)
            estimate_var = (1-kalman_gain)*prior_var # Pnn

            # Dynamics
            prior_estimate = estimate
            prior_var = estimate_var + process_noise

        return estimates



if __name__ == '__main__':
    filepathPCE = r"..\data\PnOMar-03-2023 18_12_02.csv"


    showPCEGraphs(filepathPCE)
    # ,[23,24,25,26,27,28,29,30,31]

    # filePathJV = r"..\data\scanlightMar-03-2023 17_16_10.csv"

    # # showJVGraphs(filePathJV)
    # showJVGraphs(filePathJV)
    # showJVGraphsSmoothed(filePathJV)
    # # ,[23,24,25,26,27,28,29,30,31]


# %%