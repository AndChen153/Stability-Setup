#%%
import matplotlib.pyplot as plt
import numpy as np
import numpy_indexed as npi
from labellines import labelLines
import os
import sys
from typing import List

import logging
log_name = "data_show"

NUM_PIXELS = 8

np.set_printoptions(threshold=sys.maxsize)

def show_pce_graphs_one_graph(graph_name,
                    lightScanName = "",
                    startingPoint = 0,
                    divFactor = 50,
                    show_dead_pixels = False,
                    pixels = None,
                    devices = None):
    plot_size = (12,8)
    arr = np.loadtxt(graph_name,
                     delimiter=",",
                     dtype=str)

    if lightScanName != "":
        dead_pixels = get_dead_pixels(lightScanName)
    else:
        dead_pixels = []
    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
    pce_indicies = [header_dict[value] for value in header_dict if "PCE" in value]
    arr = arr[7:, :]

    time = np.array(arr[:,header_dict["Time"]]).astype('float')
    pce_list = np.array(arr)

    png_save_location = graph_name[:-4]
    plot_title_orig = png_save_location.split("\\")[-1]
    png_save_location = png_save_location + "\\"
    if not os.path.exists(png_save_location):
        os.mkdir(png_save_location)

    pce_list = pce_list[:, pce_indicies]
    # pce_list = pce_list[:,0:-1]
    for i in range(len(pce_list)):
        pce_list[i] = [float(j) if j != " ovf" else 0.0 for j in pce_list[i]]
        pce_list[i] = [float(j) if j != "nan" else 0.0 for j in pce_list[i]]

    pce_list = pce_list.astype(float)

    data = []

    data = pce_list #np.array(data).T
    # data *= 2.048 # comment line if not using mask

    # convert to hours
    time/=3600

    min_time = min(time)*0.99
    max_time = max(time)*1.01
    max_pce = 20

    plot_title = plot_title_orig + " DEVICE_" + str(pixels)

    plt.figure(figsize=plot_size)
    plt.xlim(min_time,max_time)
    plt.ylim(bottom = -0, top = max_pce)
    plt.title(plot_title)
    plt.xlabel('Time [hrs]')
    plt.grid()

    plt.ylabel('PCE [%]')
    plt.subplots_adjust(left=0.086,
                        bottom=0.06,
                        right=0.844,
                        top=0.927,
                        wspace=0.2,
                        hspace=0.2)

    for i in range(NUM_PIXELS):
        if i in dead_pixels and not show_dead_pixels:
                continue
        lineName = "PCE" + str(i + 1)
        # print(np.array(pce_list[i]))
        plt.plot(time,data[:,i], label = lineName)

    labelLines(plt.gca().get_lines(), zorder=2.5)
    plt.legend(bbox_to_anchor=(1.15, 1))
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    return

def show_pce_graphs(graph_name,
                    lightScanName = "",
                    startingPoint = 0,
                    divFactor = 50,
                    show_dead_pixels = False,
                    pixels = None,
                    devices = None):
    plot_size = (12,8)
    arr = np.loadtxt(graph_name,
                     delimiter=",",
                     dtype=str)

    NUM_DEVICES = int((arr.shape[1]-2)/16) #subtract arduino id and time
    device_to_pixels = {}
    for i in range(NUM_DEVICES):
        device_to_pixels[i] = [j + NUM_PIXELS*i for j in range(NUM_PIXELS)]

    if lightScanName != "":
        dead_pixels = get_dead_pixels(lightScanName)
    else:
        dead_pixels = []
    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
    pce_indicies = [header_dict[value] for value in header_dict if "PCE" in value]
    arr = arr[7:, :]

    time = np.array(arr[:,header_dict["Time"]]).astype('float')
    pce_list = np.array(arr)
    average = pce_list.shape[0]/divFactor

    png_save_location = graph_name[:-4]
    plot_title_orig = png_save_location.split("\\")[-1]
    png_save_location = png_save_location + "\\"
    if not os.path.exists(png_save_location):
        os.mkdir(png_save_location)

    pce_list = pce_list[:, pce_indicies]
    # pce_list = pce_list[:,0:-1]
    for i in range(len(pce_list)):
        pce_list[i] = [float(j) if j != " ovf" else 0.0 for j in pce_list[i]]
        pce_list[i] = [float(j) if j != "nan" else 0.0 for j in pce_list[i]]

    pce_list = pce_list.astype(float)

    data = []



    data = pce_list #np.array(data).T
    # data *= 2.048 # comment line if not using mask
    time/=3600

    min_time = min(time)*0.99
    max_time = max(time)*1.01
    max_pce = 20
    logging.info(f"PC: max_time, {max_time}")
    logging.info(f"PC: max_pce, {max_pce}")


    if pixels is None and devices is None and NUM_DEVICES > 1:  # if no specific pixels have been selected
        plot_title = plot_title_orig + "ALLDEVICES"
        plt.figure(figsize=plot_size)
        plt.xlim(min_time,max_time)

        plt.ylim(bottom = -0, top = max_pce)
        plt.title(plot_title)
        logging.info(f"PC: SAVED IMAGE {plot_title}")

        plt.xlabel('Time [hrs]')
        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086,
                            bottom=0.06,
                            right=0.844,
                            top=0.927,
                            wspace=0.2,
                            hspace=0.2)
        for i in range(NUM_DEVICES):
            if i in dead_pixels and not show_dead_pixels:
                continue

            lineName = "PCE" + str(i + 1)
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
            logging.info(f"PC: SAVED IMAGE {plot_title}")
            plt.figure(figsize=plot_size)
            plt.xlim(min_time,max_time)
            plt.ylim(bottom = -0, top = max_pce)
            plt.title(plot_title)
            plt.grid()

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
                lineName = "PCE" + str(i + 1)
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
        plt.xlim(min_time,max_time)
        plt.ylim(bottom = -0, top = max_pce)
        plt.title(plot_title)
        plt.xlabel('Time [hrs]')
        plt.grid()

        plt.ylabel('PCE [%]')
        plt.subplots_adjust(left=0.086,
                            bottom=0.06,
                            right=0.844,
                            top=0.927,
                            wspace=0.2,
                            hspace=0.2)
        for i in range(NUM_DEVICES):
            pixels = device_to_pixels[i]
            for i in pixels:
                if i in dead_pixels and not show_dead_pixels:
                        continue
                lineName = "PCE" + str(i + 1)
                # print(np.array(pce_list[i]))
                plt.plot(time,data[:,i], label = lineName)

            labelLines(plt.gca().get_lines(), zorder=2.5)
            plt.legend(bbox_to_anchor=(1.15, 1))
            plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    # save all graphs
    if NUM_DEVICES > 1:
        for i in range(NUM_DEVICES):
            plot_title = plot_title_orig + " DEVICE_" + str(i)
            # plot_title = plot_title_orig + " DEVICE_AVG_" + str(i)

            logging.info(f"PC: SAVED IMAGE {plot_title}")
            plt.figure(figsize=plot_size)
            plt.xlim(min_time,max_time)
            plt.ylim(bottom = -0, top = max_pce)
            plt.title(plot_title)
            plt.grid()

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
                lineName = "PCE" + str(i + 1)
                # print(np.array(pce_list[i]))
                plt.plot(time,data[:,i], label = lineName)

        # averagePCE = np.zeros_like(np.array(data[:,i]))
        # count = 0
        # for i in pixels:
        #     if i in dead_pixel and not show_dead_pixels:
        #             continue
        #     lineName = "PCE" + str(i + 1)
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
        plt.grid()

        bp = ax.boxplot(data[-1,:])
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

def show_scan_graphs(graph_name,
                 show_dead_pixels = False,
                 pixels = None,
                 devices = None,
                 fixed_window = False):
    plot_size = (10,8)
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    NUM_DEVICES = int((arr.shape[1]-2)/16)
    device_to_pixels = {}
    for i in range(NUM_DEVICES):
        device_to_pixels[i] = [j + NUM_PIXELS*i for j in range(NUM_PIXELS)]

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
    voltage = arr[:, 1]
    length = (len(headers) - 1)


    jvList = []
    for i in range(2, length): #remove timing and voltage output from array
        jvList.append(arr[:,i])

    maxX,minX,maxY,minY= 0,0,0,0
    for i in range(0,len(jvList),2):
        # print(i)

        jvList[i] = [float(v) - 5*float(j)*0.001 for v, j in zip(jvList[i], jvList[i+1])]
        # jvList[i] = [float(j) for j in jvList[i]]
        # jvList[i+1] = [float(j) for j in jvList[i+1]]https://www.vishay.com/docs/81521/bpw34.pdf
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
        plt.title(plot_title_orig)
        plt.xlabel('Bias [V]')
        plt.ylabel('Jmeas [mAcm-2]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)
        for i in range(0,len(jvList),2):
            if int(i/2) in dead_pixel and not show_dead_pixels:
                    continue
            jvLen = len(jvList[i])//2

            lineName = "Pixel " + str(int(i/2) + 1) + " Reverse"
            plt.plot(jvList[i][0:jvLen],jvList[i+1][0:jvLen], label = lineName)

            lineName = "Pixel " + str(int(i/2) + 1) + " Forward"
            plt.plot(jvList[i][jvLen:],jvList[i+1][jvLen:], '--', label = lineName)


        ax = plt.gca()
        plt.grid()
        ax.spines['bottom'].set_position('zero')
        plt.xticks(np.arange(minX, maxX, 0.1))
        # plt.yticks(np.arange(int(minY), int(maxY), 10))
        # labelLines(plt.gca().get_lines(), zorder=2.5)

        plt.legend(bbox_to_anchor=(1.18, 1))
        plot_title = plot_title_orig
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    elif devices is not None: # show certain devices
        for i in devices:
            plot_title = plot_title_orig + " DEVICE_" + str(i)
            plt.figure(figsize=plot_size)
            plt.xlim(minX,maxX)
            plt.ylim(minY, maxY)
            plt.title(plot_title)
            plt.xlabel('Bias [V]')
            plt.ylabel('Jmeas [mAcm-2]')
            # plt.ylabel('Jmeas [mA/cm]')
            plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

            pixels = device_to_pixels[i]
            for i in pixels:
                if i in dead_pixel and not show_dead_pixels:
                    continue
                # print(i)
                i*=2
                lineName = "Pixel " + str(int(i/2) + 1)
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
        plt.ylabel('Jmeas [mAcm-2]')
        # plt.ylabel('Jmeas [mA/cm]')
        plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

        for i in pixels:
            if i in dead_pixel and not show_dead_pixels:
                    continue
            i*=2
            lineName = "Pixel " + str(int(i/2) + 1)
            plt.plot(jvList[i],jvList[i+1], label = lineName)

        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        labelLines(plt.gca().get_lines(), zorder=2.5)
        plt.legend(bbox_to_anchor=(1.18, 1))
        plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    if len(device_to_pixels) > 1:
        for i in device_to_pixels: # save all 4 devices
            plot_title = plot_title_orig + " DEVICE_" + str(i)

            logging.info(f"PC: SAVED IMAGE {plot_title}")
            plt.figure(figsize=plot_size)
            plt.xlim(minX,maxX)
            plt.ylim(minY, maxY)
            plt.title(plot_title)
            plt.xlabel('Bias [V]')
            plt.ylabel('Jmeas [mAcm-2]')
            # plt.ylabel('Jmeas [mA/cm]')
            plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

            pixels = device_to_pixels[i]
            for i in pixels:
                if i in dead_pixel and not show_dead_pixels:
                        continue
                i*=2
                lineName = "Pixel " + str(int(i/2) + 1)
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
    logging.info(f"reverseFF {np.median(reverseFF)}")
    logging.info(f"forwardFF {np.median(forwardFF)}")
    logging.info(f"reverseJSC {np.median(reverseJSC)}")
    logging.info(f"forwardJSC {np.median(forwardJSC)}")
    logging.info(f"reverseVOC {np.median(reverseVOC)}")
    logging.info(f"forwardVOC {np.median(forwardVOC)}")

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

    return png_save_location

def get_dead_pixels(graph_name) -> List[int]:
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
    jListReverse, jListForward = np.array_split(jList, 2)
    vListReverse, vListForward = np.array_split(vList, 2)

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

if __name__ == '__main__':
    # Scan = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-09-2023 13_38_40\Nov-09-2023 13_40_43lightID2scan.csv"
    # show_scan_graphs(Scan, show_dead_pixels=True,pixels= None, devices=None, fixed_window=False)

    PCE = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-05-2024 14_27_13\Nov-05-2024 14_27_13ID2PnO.csv"
    # show_pce_graphs(PCE, show_dead_pixels = True, pixels= None, devices= None)
    show_pce_graphs_one_graph(PCE, show_dead_pixels = True, pixels= None, devices= None)


# %%