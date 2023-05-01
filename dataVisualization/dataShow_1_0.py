#%%
import matplotlib.pyplot as plt
import numpy as np
import numpy_indexed as npi
from labellines import labelLines
import os
import sys

np.set_printoptions(threshold=sys.maxsize)



def showPCEGraphs(graphName, lightScanName, startingPoint = 0, divFactor = 50, showDeadPixels = False, pixels = None, devices = None):
    plotSize = (12,8)
    deviceToPixels = {0:[0,1,2,3,4,5,6,7],
                      1:[8,9,10,11,12,13,14,15],
                      2:[16,17,18,19,20,21,22,23],
                      3:[24,25,26,27,28,29,30,31]}

    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    deadPixels = getDeadPixels(lightScanName)
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    arr = arr[7:, :]

    time = arr[:,headerDict["Time"]]
    pceList = np.array(arr)
    average = pceList.shape[0]/divFactor

    pngSaveLocation = graphName[:-4]
    plotTitleOrig = pngSaveLocation.split("\\")[-1]
    pngSaveLocation = pngSaveLocation + "\\"
    if not os.path.exists(pngSaveLocation):
        os.mkdir(pngSaveLocation)

    # UNCOMMENT LINE IF CSV INCLUDES VOLTAGE AND CURRENT
    pceList = np.delete(pceList, slice(1,65), axis=1)
    pceList = pceList[:,0:-1]
    for i in range(len(pceList)):
        pceList[i] = [float(j) if j != " ovf" else 0.0 for j in pceList[i]]
        pceList[i] = [float(j) if j != "nan" else 0.0 for j in pceList[i]]

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
    # data *= 2.048 # comment line if not using mask
    time*=average
    time/=3600

    # a = a[a[:, 0].argsort()])

    maxTime = max(time)*1.01
    maxPCE = 20
    print("MAXTIME", maxTime)
    print("MAXPCE", maxPCE)


    if pixels is None and devices is None:  # if no specific pixels have been selected
        plt.figure(figsize=plotSize)
        plt.xlim(0,maxTime)

        plt.ylim(bottom = -0, top = maxPCE)
        plt.title(plotTitleOrig + "ALLDEVICES")
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)
        for i in range(data.shape[1]):
            if i in deadPixels and not showDeadPixels:
                continue

            lineName = "PCE" + str(i)
            # print(np.array(pceList[i]))
            plt.plot(time,data[:,i], label = lineName)

        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plotTitle = plotTitleOrig + "ALLDEVICES"
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')
    elif devices is not None:

        for i in devices:
            plotTitle = plotTitleOrig + " DEVICE_" + str(i)

            plt.figure(figsize=plotSize)
            plt.xlim(0,maxTime)
            plt.ylim(bottom = -0, top = maxPCE)
            plt.title(plotTitle)
            plt.xlabel('Time [hrs]')
            plt.ylabel('PCE [%]')
            plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

            pixels = deviceToPixels[i]
            for i in pixels:
                if i in deadPixels and not showDeadPixels:
                    continue
                lineName = "PCE" + str(i)
                # print(np.array(pceList[i]))
                plt.plot(time,data[:,i], label = lineName)

            labelLines(plt.gca().get_lines(), zorder=2.5)
            plt.legend(bbox_to_anchor=(1.15, 1))
            plt.savefig(pngSaveLocation+plotTitle, dpi=300, bbox_inches='tight')
    else:
        plotTitle = plotTitleOrig + " DEVICE_" + str(pixels)

        plt.figure(figsize=plotSize)
        plt.xlim(0,maxTime)
        plt.ylim(bottom = -0, top = maxPCE)
        plt.title(plotTitle)
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        for i in pixels:
            if i in deadPixels and not showDeadPixels:
                    continue
            lineName = "PCE" + str(i)
            # print(np.array(pceList[i]))
            plt.plot(time,data[:,i], label = lineName)

        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

    # save all graphs
    for i in [0,1,2,3]:
        plotTitle = plotTitleOrig + " DEVICE_" + str(i)
        # plotTitle = plotTitleOrig + " DEVICE_AVG_" + str(i)

        print("SAVED IMAGE", plotTitle)
        plt.figure(figsize=plotSize)
        plt.xlim(0,maxTime)
        plt.ylim(bottom = -0, top = maxPCE)
        plt.title(plotTitle)
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        pixels = deviceToPixels[i]
        for i in pixels:
            if i in deadPixels and not showDeadPixels:
                    continue
            lineName = "PCE" + str(i)
            # print(np.array(pceList[i]))
            plt.plot(time,data[:,i], label = lineName)

        # averagePCE = np.zeros_like(np.array(data[:,i]))
        # count = 0
        # for i in pixels:
        #     if i in deadPixels and not showDeadPixels:
        #             continue
        #     lineName = "PCE" + str(i)
        #     averagePCE += np.array(data[:,i])
        #     count += 1
        #     # print(np.array(pceList[i]))
        # averagePCE/=count
        # plt.plot(time,averagePCE, label = lineName)

        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

    plotTitle = "Γ_PCE_BoxPlot_(last values)"
    fig = plt.figure(figsize=plotSize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plotTitle)
    ax.set_ylabel('PCE (%)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(data[-1,:])
    plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

def showJVGraphsSmoothed(graphName, pixels = None):
    plotSize = (10,8)
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

    plt.figure(figsize=plotSize)
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

def showJVGraphs(graphName, showDeadPixels = False, pixels = None, devices = None):
    plotSize = (10,8)
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    deviceToPixels = {0:[0,1,2,3,4,5,6,7],
                      1:[8,9,10,11,12,13,14,15],
                      2:[16,17,18,19,20,21,22,23],
                      3:[24,25,26,27,28,29,30,31]}
    pngSaveLocation = graphName[:-4]

    plotTitleOrig = pngSaveLocation.split("\\")[-1]

    pngSaveLocation = pngSaveLocation + "\\"
    if not os.path.exists(pngSaveLocation):
        os.mkdir(pngSaveLocation)
    deadPixels = getDeadPixels(graphName)
    # graphName = graphName.split('\\')
    headers = arr[6,:]
    headerDict = {value: index for index, value in enumerate(headers)}
    arr = arr[7:, :]
    length = (len(headers) - 1)


    jvList = []
    for i in range(2, length): #remove timing and voltage output from array
        jvList.append(arr[:,i])




    maxX,minX,maxY,minY= 0,0,0,0
    for i in range(0,len(jvList),2):
        # print(i)
        jvList[i] = [float(j) for j in jvList[i]]
        jvList[i+1] = [float(x)/0.128 for x in jvList[i+1]]
        # jvList[i+1] = [float(x) / 0.0625 for x in jvList[i+1]]

        if max(jvList[i]) > maxX: maxX = max(jvList[i])
        if min(jvList[i]) < minX: minX = min(jvList[i])
        if max(jvList[i+1]) > maxY: maxY = max(jvList[i+1])
        if min(jvList[i+1]) < minY: minY = min(jvList[i+1])
    # print(jvList)
    # maxX *= 1.1

    # minX *= 1.1
    # maxY *= 1.1
    # minY *= 1.1
    maxX = 1.3
    minX = 0
    maxY = 26
    minY = -2
    # print(maxX,minX,maxY,minY)


    # generate graphs
    if pixels is None and devices is None: # show all pixels
        plt.figure(figsize=plotSize)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plotTitleOrig + "ALLDEVICES")
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)
        for i in range(0,len(jvList),2):
            # print(deadPixels, showDeadPixels)
            if int(i/2) in deadPixels and not showDeadPixels:
                    continue
            # print(i)
            lineName = "Pixel " + str(int(i/2))
            # print(jvList[i],jvList[i+1])
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)

        plt.legend(bbox_to_anchor=(1.18, 1))
        plotTitle = plotTitleOrig + "ALLDEVICES"
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

    elif devices is not None: # show certain devices
        print(" DEVICES")

        for i in devices:
            plotTitle = plotTitleOrig + " DEVICE_" + str(i)
            plt.figure(figsize=plotSize)
            plt.xlim(minX,maxX)
            plt.ylim(minY, maxY)
            plt.title(plotTitle)
            plt.xlabel('Bias [V]')
            plt.ylabel('Current [mA]')
            # plt.ylabel('Jmeas [mA/cm]')
            plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

            pixels = deviceToPixels[i]
            for i in pixels:
                if i in deadPixels and not showDeadPixels:
                    continue
                # print(i)
                i*=2
                lineName = "Pixel " + str(int(i/2))
                plt.plot(jvList[i],jvList[i+1], label = lineName)

            ax = plt.gca()
            ax.spines['bottom'].set_position('zero')
            labelLines(plt.gca().get_lines(), zorder=2.5)
            plt.legend(bbox_to_anchor=(1.18, 1))
            plt.savefig(pngSaveLocation+plotTitle, dpi=300, bbox_inches='tight')

    elif pixels is not None: # show certain pixels
        plotTitle = plotTitleOrig + " DEVICE_" + str(pixels)
        # pngTitle += " PIXELS" + "_".join(str(x) for x in pixels)
        plt.figure(figsize=plotSize)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plotTitle)
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        for i in pixels:
            if i in deadPixels and not showDeadPixels:
                    continue
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.18, 1))
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')


    for i in [0,1,2,3]: # save all 4 devices
        plotTitle = plotTitleOrig + " DEVICE_" + str(i)

        print("SAVED IMAGE", plotTitle)
        plt.figure(figsize=plotSize)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plotTitle)
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        pixels = deviceToPixels[i]
        for i in pixels:
            if i in deadPixels and not showDeadPixels:
                    continue
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.18, 1))
        plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

    # generate boxplots
    reverse, forward = scanCalcs(graphName)
    # returns: reverse:[fillFactorListSplit, jscListSplit, vocListSplit], forward:[fillFactorListSplit, jscListSplit, vocListSplit]
    reverseFF = reverse[0]
    forwardFF = forward[0]
    reverseJSC = reverse[1]
    forwardJSC = forward[1]
    reverseVOC = reverse[2]
    forwardVOC = forward[2]
    print("reverseFF", np.median(reverseFF))
    print("forwardFF", np.median(forwardFF))
    print("reverseJSC", np.median(reverseJSC))
    print("forwardJSC", np.median(forwardJSC))
    print("reverseVOC", np.median(reverseVOC))
    print("forwardVOC", np.median(forwardVOC))

    FF = [np.array(reverseFF).flatten(), np.array(forwardFF).flatten()]
    JSC = [np.array(reverseJSC).flatten(), np.array(forwardJSC).flatten()]
    VOC = [np.array(reverseVOC).flatten(), np.array(forwardVOC).flatten()]

    plotTitle = "Γ_FF_BoxPlot"
    fig = plt.figure(figsize=plotSize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plotTitle)
    ax.set_ylabel('FF (%)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(FF)
    plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')


    plotTitle = "Γ_JSC_BoxPlot"
    fig = plt.figure(figsize=plotSize)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plotTitle)
    ax.set_ylabel('Jsc (mA/cm2)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(JSC)
    plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')

    plotTitle = "Γ_VOC_BoxPlot"
    fig = plt.figure(figsize=plotSize)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plotTitle)
    ax.set_ylabel('Voc (V)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(VOC)
    plt.savefig(pngSaveLocation + plotTitle, dpi=300, bbox_inches='tight')






def getDeadPixels(graphName):
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    headers = arr[6,:]
    arr = arr[7:, :]

    # print(arr)
    length = (len(headers) - 1)


    jvList = []
    for i in range(2, length): # remove timing and volts output
        jvList.append(arr[:,i])

    deadPixels = []
    for i in range(0,len(jvList),2):
        # print(i)
        # print(jvList[i], jvList[i+1])
        jvList[i] = [float(j) for j in jvList[i]]
        jvList[i+1] = [float(x) for x in jvList[i+1]]
        if np.mean(np.absolute(np.array(jvList[i]))) < 0.2 or np.mean(np.absolute(np.array(jvList[i+1]))) < 0.2:
            deadPixels.append(int(i/2))#[9, 12, 13, 19, 21, 27, 30, 31]


    return deadPixels


def scanCalcs(graphName):
    '''
    returns: reverse:[fillFactorListSplit, jscListSplit, vocListSplit], forward:[fillFactorListSplit, jscListSplit, vocListSplit]
    '''
    arr = np.loadtxt(graphName, delimiter=",", dtype=str)
    deadPixels = getDeadPixels(graphName)
    # print(deadPixels)
    graphName = graphName.split('\\')
    # print(arr)

    headers = arr[6,:]

    headerDict = {value: index for index, value in enumerate(headers)}
    # print(headerDict)
    arr = arr[7:, :]
    length = (len(headers) - 1)
    # print(length)

    jvList = []

    for i in range(2, length):
        jvList.append(arr[:,i])


    jList = [] #current
    vList = [] #voltage
    for i in range(0,len(jvList),2):
        # print(i)
        jList.append([float(j) for j in jvList[i+1]])
        vList.append([float(x) for x in jvList[i]])
        # jvList[i+1] = [float(x) / 0.128 for x in jvList[i+1]]

    jList = np.array(jList).T
    vList = np.array(vList).T
    jListReverse, jListForward = np.split(jList, 2)
    vListReverse, vListForward = np.split(vList, 2)

    def calc(jList, vList):



        # find Jsc (V = 0)
        jscList = np.zeros((vList.shape[1]))
        for i in range(vList.shape[1]):
            difference_array = np.absolute(vList[:,i])
            idx = difference_array.argmin()
            jscList[i] = jList[idx,i]

        # find Voc (J = 0)
        vocList = np.zeros((jList.shape[1]))
        for i in range(jList.shape[1]):
            difference_array = np.absolute(jList[:,i])
            idx = difference_array.argmin()
            vocList[i] = vList[idx,i]

        # find Fill Factor
        pceList = jList*vList
        # print(np.array(pceList).shape)
        maxVIdx = np.argmax(pceList, axis=0) # find index of max pce value
        # print(np.array(maxVIdx).shape)
        vmppList = []
        jmppList = []
        for i in range(len(maxVIdx)): # for i in number of pixels
            # if vList[maxVIdx[i],i]>0:
            vmppList.append(vList[maxVIdx[i],i])
            jmppList.append(jList[maxVIdx[i],i])
        vmppList = np.array(vmppList)
        jmppList = np.array(jmppList)

        fillFactorList = 100*vmppList*jmppList/(jscList*vocList)
        jscList = jscList/0.128
        # jscList = jscList/0.0625

        deviceToPixels = {0:[0,1,2,3,4,5,6,7],
                        1:[8,9,10,11,12,13,14,15],
                        2:[16,17,18,19,20,21,22,23],
                        3:[24,25,26,27,28,29,30,31]}


        fillFactorList = np.delete(fillFactorList, deadPixels)
        jscList = np.delete(jscList, deadPixels)
        vocList = np.delete(vocList, deadPixels)


        # fillFactorListSplit = []
        # jscListSplit = []
        # vocListSplit = []

        # for i in [0,1,2,3]:
        #     alive = []
        #     for i in deviceToPixels[i]:
        #         # if i not in deadPixels:
        #         alive.append(i)
        #     # print(alive)
        #     fillFactorListSplit.append([fillFactorList[alive]])
        #     jscListSplit.append([jscList[alive]])
        #     vocListSplit.append([vocList[alive]])

        # fillFactorList, jscList, vocList
        return (fillFactorList, jscList, vocList)

    return calc(jListReverse, vListReverse), calc(jListForward, vListForward)

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
    # arr = np.loadtxt(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\PnOMar-15-2023 13_29_55.csv", delimiter=",", dtype=str)[0:5,0:2]
    # print(arr)
    PCE = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Apr-25-2023 15_50_01\Apr-25-2023 15_51_12PnO.csv"

    Scan = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Apr-25-2023 15_50_01\Apr-25-2023 15_50_06lightscan.csv"
    showJVGraphs(Scan, showDeadPixels=False,pixels= None, devices=None)
    showPCEGraphs(PCE, Scan, showDeadPixels = False, pixels= None, devices= None)



# %%