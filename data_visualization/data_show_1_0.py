#%%
import matplotlib.pyplot as plt
import numpy as np
import numpy_indexed as npi
from labellines import labelLines
import os
import sys

np.set_printoptions(threshold=sys.maxsize)


def show_pce_graphs(graph_name,
                    lightScanName,
                    startingPoint = 0,
                    divFactor = 50,
                    show_dead_pixels = False,
                    pixels = None,
                    devices = None):
    plot_size = (12,8)
    device_to_pixels = {0:[0,1,2,3,4,5,6,7],
                      1:[8,9,10,11,12,13,14,15],
                      2:[16,17,18,19,20,21,22,23],
                      3:[24,25,26,27,28,29,30,31]}

    arr = np.loadtxt(graph_name,
                     delimiter=",",
                     dtype=str)
    dead_pixels = get_dead_pixels(lightScanName)
    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
    arr = arr[7:, :]

    time = arr[:,header_dict["Time"]]
    pce_list = np.array(arr)
    average = pce_list.shape[0]/divFactor

    png_save_location = graph_name[:-4]
    plot_title_orig = png_save_location.split("\\")[-1]
    png_save_location = png_save_location + "\\"
    if not os.path.exists(png_save_location):
        os.mkdir(png_save_location)

    # UNCOMMENT LINE IF CSV INCLUDES VOLTAGE AND CURRENT
    pce_list = np.delete(pce_list, slice(1,65), axis=1)
    pce_list = pce_list[:,0:-1]
    for i in range(len(pce_list)):
        pce_list[i] = [float(j) if j != " ovf" else 0.0 for j in pce_list[i]]
        pce_list[i] = [float(j) if j != "nan" else 0.0 for j in pce_list[i]]

    pce_list = pce_list.astype(float)
    # print(pce_list)

    pce_list[:,0] = np.floor(pce_list[:,0]/average)
    time = np.unique(pce_list[:,0])
    data = []
    # print(len(time))


    # print(len(npi.group_by(pce_list[:, 0]).split(pce_list[:, 8])))
    for i in range(1,pce_list.shape[1]):
        avg = []
        col_split = npi.group_by(pce_list[:, 0]).split(pce_list[:, i])
        for i in col_split:
            avg.append(np.average(i))
        data.append(avg)
    time = np.array(time)
    data = np.array(data).T
    # data *= 2.048 # comment line if not using mask
    time*=average
    time/=3600

    # a = a[a[:, 0].argsort()])

    max_time = max(time)*1.01
    max_pce = 20
    print("max_time", max_time)
    print("max_pce", max_pce)


    if pixels is None and devices is None:  # if no specific pixels have been selected
        plt.figure(figsize=plot_size)
        plt.xlim(0,max_time)

        plt.ylim(bottom = -0, top = max_pce)
        plt.title(plot_title_orig + "ALLDEVICES")
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086,
                            bottom=0.06,
                            right=0.844,
                            top=0.927,
                            wspace=0.2,
                            hspace=0.2)
        for i in range(data.shape[1]):
            if i in dead_pixels and not show_dead_pixels:
                continue

            lineName = "PCE" + str(i)
            # print(np.array(pce_list[i]))
            plt.plot(time,data[:,i], label = lineName)

        labelLines(plt.gca().get_lines(),
                   zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plot_title = plot_title_orig + "ALLDEVICES"
        plt.savefig(png_save_location + plot_title,
                    dpi=300,
                    bbox_inches='tight')
    elif devices is not None:

        for i in devices:
            plot_title = plot_title_orig + " DEVICE_" + str(i)

            plt.figure(figsize=plot_size)
            plt.xlim(0,max_time)
            plt.ylim(bottom = -0, top = max_pce)
            plt.title(plot_title)
            plt.xlabel('Time [hrs]')
            plt.ylabel('PCE [%]')
            plt.subplots_adjust(left=0.086,
                                bottom=0.06,
                                right=0.844,
                                top=0.927,
                                wspace=0.2,
                                hspace=0.2)

            pixels = device_to_pixels[i]
            for i in pixels:
                if i in dead_pixels and not show_dead_pixels:
                    continue
                lineName = "PCE" + str(i)
                # print(np.array(pce_list[i]))
                plt.plot(time,data[:,i],
                         label = lineName)

            labelLines(plt.gca().get_lines(),
                       zorder=2.5)
            plt.legend(bbox_to_anchor=(1.15, 1))
            plt.savefig(png_save_location+plot_title,
                        dpi=300,
                        bbox_inches='tight')
    else:
        plot_title = plot_title_orig + " DEVICE_" + str(pixels)

        plt.figure(figsize=plot_size)
        plt.xlim(0,max_time)
        plt.ylim(bottom = -0, top = max_pce)
        plt.title(plot_title)
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086,
                            bottom=0.06,
                            right=0.844,
                            top=0.927,
                            wspace=0.2,
                            hspace=0.2)

        for i in pixels:
            if i in dead_pixels and not show_dead_pixels:
                    continue
            lineName = "PCE" + str(i)
            # print(np.array(pce_list[i]))
            plt.plot(time,data[:,i], label = lineName)

        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    # save all graphs
    for i in [0,1,2,3]:
        plot_title = plot_title_orig + " DEVICE_" + str(i)
        # plot_title = plot_title_orig + " DEVICE_AVG_" + str(i)

        print("SAVED IMAGE", plot_title)
        plt.figure(figsize=plot_size)
        plt.xlim(0,max_time)
        plt.ylim(bottom = -0, top = max_pce)
        plt.title(plot_title)
        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086,
                            bottom=0.06,
                            right=0.844,
                            top=0.927,
                            wspace=0.2,
                            hspace=0.2)

        pixels = device_to_pixels[i]
        for i in pixels:
            if i in dead_pixels and not show_dead_pixels:
                    continue
            lineName = "PCE" + str(i)
            # print(np.array(pce_list[i]))
            plt.plot(time,data[:,i], label = lineName)

        # averagePCE = np.zeros_like(np.array(data[:,i]))
        # count = 0
        # for i in pixels:
        #     if i in dead_pixel and not show_dead_pixels:
        #             continue
        #     lineName = "PCE" + str(i)
        #     averagePCE += np.array(data[:,i])
        #     count += 1
        #     # print(np.array(pce_list[i]))
        # averagePCE/=count
        # plt.plot(time,averagePCE, label = lineName)

        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.15, 1))
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    plot_title = "Γ_PCE_BoxPlot_(last values)"
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('PCE (%)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(data[-1,:])
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

def show_jv_graphs(graph_name,
                 show_dead_pixels = False,
                 pixels = None,
                 devices = None,
                 fixed_window = False):
    plot_size = (10,8)
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    device_to_pixels = {0:[0,1,2,3,4,5,6,7],
                      1:[8,9,10,11,12,13,14,15],
                      2:[16,17,18,19,20,21,22,23],
                      3:[24,25,26,27,28,29,30,31]}
    png_save_location = graph_name[:-4]

    plot_title_orig = png_save_location.split("\\")[-1]

    png_save_location = png_save_location + "\\"
    if not os.path.exists(png_save_location):
        os.mkdir(png_save_location)
    dead_pixel = get_dead_pixels(graph_name)
    # graph_name = graph_name.split('\\')
    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
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

    if not fixed_window:
        maxX *= 1.1
        minX *= 1.1
        maxY *= 1.1
        minY *= 1.1
    else:
        maxX = 1.3
        minX = 0
        maxY = 26
        minY = -2
    # print(maxX,minX,maxY,minY)


    # generate graphs
    if pixels is None and devices is None: # show all pixels
        plt.figure(figsize=plot_size)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plot_title_orig + "ALLDEVICES")
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)
        for i in range(0,len(jvList),2):
            # print(dead_pixel, show_dead_pixels)
            if int(i/2) in dead_pixel and not show_dead_pixels:
                    continue
            # print(i)
            lineName = "Pixel " + str(int(i/2))
            # print(jvList[i],jvList[i+1])
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)

        plt.legend(bbox_to_anchor=(1.18, 1))
        plot_title = plot_title_orig + "ALLDEVICES"
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    elif devices is not None: # show certain devices
        print(" DEVICES")

        for i in devices:
            plot_title = plot_title_orig + " DEVICE_" + str(i)
            plt.figure(figsize=plot_size)
            plt.xlim(minX,maxX)
            plt.ylim(minY, maxY)
            plt.title(plot_title)
            plt.xlabel('Bias [V]')
            plt.ylabel('Current [mA]')
            # plt.ylabel('Jmeas [mA/cm]')
            plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

            pixels = device_to_pixels[i]
            for i in pixels:
                if i in dead_pixel and not show_dead_pixels:
                    continue
                # print(i)
                i*=2
                lineName = "Pixel " + str(int(i/2))
                plt.plot(jvList[i],jvList[i+1], label = lineName)

            ax = plt.gca()
            ax.spines['bottom'].set_position('zero')
            labelLines(plt.gca().get_lines(), zorder=2.5)
            plt.legend(bbox_to_anchor=(1.18, 1))
            plt.savefig(png_save_location+plot_title, dpi=300, bbox_inches='tight')

    elif pixels is not None: # show certain pixels
        plot_title = plot_title_orig + " DEVICE_" + str(pixels)
        # pngTitle += " PIXELS" + "_".join(str(x) for x in pixels)
        plt.figure(figsize=plot_size)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plot_title)
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        for i in pixels:
            if i in dead_pixel and not show_dead_pixels:
                    continue
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.18, 1))
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')


    for i in [0,1,2,3]: # save all 4 devices
        plot_title = plot_title_orig + " DEVICE_" + str(i)

        print("SAVED IMAGE", plot_title)
        plt.figure(figsize=plot_size)
        plt.xlim(minX,maxX)
        plt.ylim(minY, maxY)
        plt.title(plot_title)
        plt.xlabel('Bias [V]')
        plt.ylabel('Current [mA]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        pixels = device_to_pixels[i]
        for i in pixels:
            if i in dead_pixel and not show_dead_pixels:
                    continue
            i*=2
            lineName = "Pixel " + str(int(i/2))
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.18, 1))
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    # generate boxplots
    reverse, forward = scan_calcs(graph_name)
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

    plot_title = "Γ_FF_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('FF (%)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(FF)
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')


    plot_title = "Γ_JSC_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('Jsc (mA/cm2)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(JSC)
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    plot_title = "Γ_VOC_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('Voc (V)')
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(VOC)
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')






def get_dead_pixels(graph_name):
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    headers = arr[6,:]
    arr = arr[7:, :]

    # print(arr)
    length = (len(headers) - 1)


    jvList = []
    for i in range(2, length): # remove timing and volts output
        jvList.append(arr[:,i])

    dead_pixels = []
    for i in range(0,len(jvList),2):
        # print(i)
        # print(jvList[i], jvList[i+1])
        jvList[i] = [float(j) for j in jvList[i]]
        jvList[i+1] = [float(x) for x in jvList[i+1]]
        if np.mean(np.absolute(np.array(jvList[i]))) < 0.2 or np.mean(np.absolute(np.array(jvList[i+1]))) < 0.2:
            dead_pixels.append(int(i/2))#[9, 12, 13, 19, 21, 27, 30, 31]


    return dead_pixels


def scan_calcs(graph_name):
    '''
    returns: reverse:[fillFactorListSplit, jscListSplit, vocListSplit], forward:[fillFactorListSplit, jscListSplit, vocListSplit]
    '''
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    dead_pixels = get_dead_pixels(graph_name)
    # print(dead_pixels)
    graph_name = graph_name.split('\\')
    # print(arr)

    headers = arr[6,:]

    header_dict = {value: index for index, value in enumerate(headers)}
    # print(header_dict)
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
        pce_list = jList*vList
        # print(np.array(pce_list).shape)
        maxVIdx = np.argmax(pce_list, axis=0) # find index of max pce value
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

        device_to_pixels = {0:[0,1,2,3,4,5,6,7],
                        1:[8,9,10,11,12,13,14,15],
                        2:[16,17,18,19,20,21,22,23],
                        3:[24,25,26,27,28,29,30,31]}


        fillFactorList = np.delete(fillFactorList, dead_pixels)
        jscList = np.delete(jscList, dead_pixels)
        vocList = np.delete(vocList, dead_pixels)


        # fillFactorListSplit = []
        # jscListSplit = []
        # vocListSplit = []

        # for i in [0,1,2,3]:
        #     alive = []
        #     for i in device_to_pixels[i]:
        #         # if i not in dead_pixels:
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


def show_jv_graphsSmoothed(graph_name, pixels = None):
    plot_size = (10,8)
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    graph_name = graph_name.split('\\')
    # print(arr)
    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
    # print(header_dict)
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
    #     col_split = npi.group_by(jvList[:, 0]).split(jvList[:, i])
    #     for i in col_split:
    #         avg.append(np.average(i))
    #     data.append(avg)
    jvList = np.array(jvList).T
    data = jvList

    print(jvList.shape)
    # print(len(npi.group_by(pce_list[:, 0]).split(pce_list[:, 8])))
    for i in range(0,jvList.shape[1],2):
        # print(jvList[:, i+1])

        # print(kalmanFilter(jvList[:, i+1]))
        jvList[:, i+1] = kalmanFilter(jvList[:, i+1])
        # break
    # print(np.array(data).T.shape)
    jvList = np.array(data).T

    plt.figure(figsize=plot_size)
    plt.xlim(minX,maxX)
    plt.ylim(minY, maxY)
    plt.title(graph_name[-1][:-4])
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


if __name__ == '__main__':
    # PCE = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Apr-25-2023 15_50_01\Apr-25-2023 15_51_12PnO.csv"
    Scan = r"C:\Users\Andrew Chen\Dropbox\code\Stability-Setup\data\Aug-22-2023 00_08_28\Aug-22-2023 00_10_18lightscan.csv"

    show_jv_graphs(Scan, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)
    # show_pce_graphs(PCE, Scan, show_dead_pixels = False, pixels= None, devices= None)

# %%