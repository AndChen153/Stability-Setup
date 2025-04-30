#%%
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend to suppress GUI errors

import matplotlib.pyplot as plt
import numpy as np
from labellines import labelLines
import os
import sys
import warnings
from typing import List
from helper.global_helpers import logger
from matplotlib.font_manager import FontProperties
import matplotlib.ticker as ticker

NUM_PIXELS = 8
np.set_printoptions(threshold=sys.maxsize)

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
warnings.filterwarnings("ignore", category=RuntimeWarning)

def plot_all_in_folder(directory_path):
    all_files = load_unplotted_files(directory_path)
    for filepath in all_files:
        create_graph(filepath)
    return

def create_graph(file_location):
    if (file_location.endswith("scan.csv")):
        logger.log(f"Creating Plots for: {file_location}")
        create_scan_graph(file_location, current_density=False)
        return create_scan_graph(file_location, current_density=True, saveInFolder = False)
    elif (file_location.endswith("mppt.csv")):
        logger.log(f"Creating Plot for: {file_location}")
        return create_pce_graph(file_location)
    else:
        return ""

def create_pce_graph(file_location,
                    lightScanName = "",
                    startingPoint = 0,
                    divFactor = 50,
                    show_dead_pixels = False,
                    pixels = None,
                    devices = None):
    plot_size = (12,8)
    arr = np.loadtxt(file_location,
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

    png_save_location = "/".join(file_location.replace('\\', '/').split('/')[:-1])
    plot_title = file_location.replace('\\', '/').split('/')[-1][:-4]
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
        # logger.log(np.array(pce_list[i]))
        plt.plot(time,data[:,i], label = lineName)

    lines = plt.gca().get_lines()
    x_min, x_max = plt.xlim()
    num_lines = len(lines)
    xvals = np.linspace(x_min + 0.1 * (x_max - x_min), x_max - 0.1 * (x_max - x_min), num_lines)
    bold_font = FontProperties(weight='medium')
    labelLines(
        lines,
        xvals=xvals,
        zorder=2.5,
        align=False,
        fontsize=11,
        fontproperties=bold_font
    )
    plt.legend(bbox_to_anchor=(1.15, 1))
    plt.savefig(png_save_location + plot_title, dpi=300, bbox_inches='tight')

    return png_save_location

def create_scan_graph(file_location,
                 current_density = True,
                 saveInFolder = True,
                 show_dead_pixels = False,
                 fixed_window = False):
    plot_size = (10,8)
    arr = np.loadtxt(file_location, delimiter=",", dtype=str)

    # logger.log("PC -> Graph Name", graph_name)
    if saveInFolder:
        png_save_location = file_location[:-4]
    else:
        png_save_location = "/".join(file_location.replace('\\', '/').split('/')[:-1])

    png_save_dir = png_save_location + "\\"
    if not os.path.exists(png_save_dir):
        os.mkdir(png_save_dir)

    box_plot_save_dir =file_location[:-4] + "\\"

    plot_title = file_location.replace('\\', '/').split('/')[-1][:-4]
    plot_title += '_Jmeas' if current_density else '_Current'

    png_save_path = png_save_dir + plot_title
    dead_pixel = get_dead_pixels(file_location)

    headers = arr[6,:]
    header_dict = {value: index for index, value in enumerate(headers)}
    arr = arr[7:, :]
    voltage = arr[:, 1]
    time = arr[:, 0]
    length = (len(headers) - 1)
    data = arr[:, 2:-1]

    pixel_V = data[:, ::2].astype(float)  # Selects even columns (0, 2, ...)
    pixel_mA = data[:, 1::2].astype(float) # Selects odd columns (1, 3, ...)
    if current_density:
        pixel_mA/=0.128

    # generate graphs
    plt.figure(figsize=plot_size)
    plt.title(plot_title)
    plt.xlabel('Bias [V]')
    if current_density:
        plt.ylabel('Jmeas [mAcm-2]')
    else:
        plt.ylabel('current [mA]')

    plt.subplots_adjust(left=0.086, bottom=0.06, right=0.844, top=0.927, wspace=0.2, hspace=0.2)

    jvLen = pixel_V.shape[0]//2
    for i in range(0,pixel_V.shape[1]):
        lineName = "Pixel " + str(i + 1) + " Reverse"
        plt.plot(pixel_V[0:jvLen, i],pixel_mA[0:jvLen, i], label = lineName)

        lineName = "Pixel " + str(i + 1) + " Forward"
        plt.plot(pixel_V[jvLen:, i],pixel_mA[jvLen:, i], '--', label = lineName)

    ax = plt.gca()
    plt.grid()
    ax.spines['bottom'].set_position('zero')
    plt.legend(bbox_to_anchor=(1.18, 1))
    plt.savefig(png_save_path, dpi=300, bbox_inches='tight')

    # generate boxplots
    reverse, forward = scan_calcs(file_location)
    # returns: reverse:[fillFactorListSplit, jscListSplit, vocListSplit], forward:[fillFactorListSplit, jscListSplit, vocListSplit]
    reverseFF = reverse[0]
    forwardFF = forward[0]
    reverseJSC = reverse[1]
    forwardJSC = forward[1]
    reverseVOC = reverse[2]
    forwardVOC = forward[2]

    FF = [np.array(reverseFF).flatten(), np.array(forwardFF).flatten()]
    JSC = [np.array(reverseJSC).flatten(), np.array(forwardJSC).flatten()]
    VOC = [np.array(reverseVOC).flatten(), np.array(forwardVOC).flatten()]

    plot_title = "Γ_FF_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('FF (%)')
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(FF)
    plt.savefig(box_plot_save_dir + plot_title, dpi=300, bbox_inches='tight')


    plot_title = "Γ_JSC_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('Jsc (mA/cm2)')
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(JSC)
    plt.savefig(box_plot_save_dir + plot_title, dpi=300, bbox_inches='tight')

    plot_title = "Γ_VOC_BoxPlot"
    fig = plt.figure(figsize=plot_size)
    # Creating axes instance
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title(plot_title)
    ax.set_ylabel('Voc (V)')
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Reverse","Forward"])
    bp = ax.boxplot(VOC)
    plt.savefig(box_plot_save_dir + plot_title, dpi=300, bbox_inches='tight')

    return png_save_dir

def get_dead_pixels(graph_name) -> List[int]:
    arr = np.loadtxt(graph_name, delimiter=",", dtype=str)
    headers = arr[6,:]
    arr = arr[7:, :]

    # logger.log(arr)
    length = (len(headers) - 1)

    jvList = []
    for i in range(2, length): # remove timing and volts output
        jvList.append(arr[:,i])

    dead_pixels = []
    for i in range(0,len(jvList),2):
        # logger.log(i)
        # logger.log(jvList[i], jvList[i+1])
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
    # logger.log(dead_pixels)
    graph_name = graph_name.split('\\')
    # logger.log(arr)

    headers = arr[6,:]

    header_dict = {value: index for index, value in enumerate(headers)}
    # logger.log(header_dict)
    arr = arr[7:, :]
    length = (len(headers) - 1)
    # logger.log(length)

    jvList = []

    for i in range(2, length):
        jvList.append(arr[:,i])


    jList = [] #current
    vList = [] #voltage
    for i in range(0,len(jvList),2):
        # logger.log(i)
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
        # logger.log(np.array(pce_list).shape)
        maxVIdx = np.argmax(pce_list, axis=0) # find index of max pce value
        # logger.log(np.array(maxVIdx).shape)
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

        # fillFactorList, jscList, vocList
        return (fillFactorList, jscList, vocList)

    return calc(jListReverse, vListReverse), calc(jListForward, vListForward)

def list_files_in_directory(directory):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepaths.append(os.path.join(root, file))
    return filepaths

def load_unplotted_files(directory):
    files = list_files_in_directory(directory)
    csv_files = [file for file in files if file.endswith(".csv")]
    png_files = [file for file in files if file.endswith(".png")]
    unplotted = []

    for csv_file in csv_files:
        csv_base_name = extract_base_name(csv_file)
        unfound = True
        for png_file in png_files:
            png_base_name = extract_base_name(png_file)

            if csv_base_name == png_base_name:
                csv_mtime = os.path.getmtime(csv_file)
                png_mtime = os.path.getmtime(png_file)
                if csv_mtime > png_mtime:
                    logger.log(csv_mtime, png_mtime)
                    unplotted.append(csv_file)
                unfound = False
                break
        if unfound:
            unplotted.append(csv_file)

    return unplotted

def extract_base_name(file_path):
    base_name = os.path.basename(file_path)
    base_name = os.path.splitext(base_name)[0]
    if "_Jmeas" in base_name:
        base_name = base_name.replace("_Jmeas", "")

    return base_name

if __name__ == '__main__':
    directory_path = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-19-2024 17_01_11 copy"
    all_files = list_files_in_directory(directory_path)

    for filepath in all_files:
        create_graph(filepath)

    # directory_path = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-20-2024 11_58_21"
    # all_files = list_files_in_directory(directory_path)

    # for filepath in all_files:
    #     show_pce_graphs_one_graph(filepath, show_dead_pixels = True, pixels= None, devices= None)


    # PCE = r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-10-2024 23_12_36\Nov-10-2024 23_12_36ID2PnO.csv"
    # # show_pce_graphs(PCE, show_dead_pixels = True, pixels= None, devices= None)
    # show_pce_graphs_one_graph(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-19-2024 13_53_16\Nov-19-2024 13_53_18ID1PnO.csv", show_dead_pixels = True, pixels= None, devices= None)
    # show_pce_graphs_one_graph(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-19-2024 13_53_16\Nov-19-2024 13_53_18ID2PnO.csv", show_dead_pixels = True, pixels= None, devices= None)
    # show_pce_graphs_one_graph(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-19-2024 13_53_16\Nov-19-2024 13_53_18ID3PnO.csv", show_dead_pixels = True, pixels= None, devices= None)
    # show_pce_graphs_one_graph(r"C:\Users\achen\Dropbox\code\Stability-Setup\data\Nov-19-2024 13_53_16\Nov-19-2024 13_53_18ID4PnO.csv", show_dead_pixels = True, pixels= None, devices= None)


# %%