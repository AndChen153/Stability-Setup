#%%
import matplotlib.pyplot as plt
import numpy as np


def showPCEGraphs(graphName):
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    graphName = graphName.split('\\')
    headers = arr[5,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    arr = arr[6:, :]


    time = arr[:,headerDict["Time"]]
    pceList = []


    for i in range(headerDict["Pixel 0 PCE"], (headerDict["Pixel 7 PCE"]+1)):
        pceList.append(arr[:,i])

    # print(pceList)

    time = [float(i) for i in time]

    maxTime = max(time)*1.01
    maxPCE = 15
    for i in range(len(pceList)):
        pceList[i] = [float(j) for j in pceList[i]]
    #     if max(pceList[i]) > maxPCE:
    #         maxPCE = max(pceList[i])

    plt.figure(figsize=(10, 8))
    # ax = plt.gca()
    # ax.set_xlim([0,maxTime])
    # ax.set_ylim(top=15)

    plt.xlim(0,maxTime/60/60)
    print(maxTime/60/60)
    plt.ylim(bottom = -0, top = 15)
    plt.title(graphName[-1][:-4])
    plt.xlabel('Time [hrs]')
    plt.ylabel('PCE [%]')
    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)


    for i in range(len(pceList)):
        lineName = "PCE" + str(i)
        print(np.array(pceList[i]))
        # plt.plot(time,pceList[i], label = lineName)
        plt.plot(np.array(time)/60/60,kalmanFilter(predictions = np.array(pceList[i]),process_noise=0.003, measurement_var=0.0055), label = lineName)
        
        # plt.plot(np.array(time)/60/60,kalmanFilter(predictions = np.array(pceList[i]),process_noise=0.1, measurement_var=0.1), label = lineName)



    plt.legend(bbox_to_anchor=(1.15, 0.65))
    plt.show()

def showJVGraphs(graphName):
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    graphName = graphName.split('\\')
    print(arr)
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[6:, :]


    jvList = []

    for i in range(1, 17):
        jvList.append(arr[:,i])


    maxX = 0
    minX = 0
    maxY = 0
    minY = 0

    for i in range(0,len(jvList),2):
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


    # f = plt.figure()
    # f.set_figwidth(10)
    # f.set_figheight(10)



    plt.figure(figsize=(10, 8))
    plt.xlim(minX,maxX)
    plt.ylim(minY, maxY)
    plt.title(graphName[-1][:-4])
    plt.xlabel('Bias [V]')
    plt.ylabel('Current [mA]')
    # plt.ylabel('Jmeas [mA/cm]')
    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)


    for i in range(0,len(jvList),2):
        lineName = "Pixel " + str(int(i/2))
        plt.plot(jvList[i],jvList[i+1], label = lineName)

    ax = plt.gca()
    ax.spines['bottom'].set_position('zero')

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
    filepathPCE = r"..\data\PnODec-13-2022 19_43_10.csv"

    showPCEGraphs(filepathPCE)

    filePathJV = r"..\data\scanlightDec-14-2022 12_41_50.csv"

    showJVGraphs(filePathJV)


# %%
