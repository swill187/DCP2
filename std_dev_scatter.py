from lembox_visualization import drawStdDev, readLemboxData
import matplotlib.pyplot as plt
import sys
import os
from tkinter import filedialog

def selectParent():
    if len(sys.argv) == 2:
        folder_path = sys.argv[1]
    else:
        print("Please select the parent folder...")
        folder_path = filedialog.askdirectory()
    
    if not folder_path:
        print("No folder selected. Exiting...")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)

    return folder_path

def searchDir(dir):
    data_folders = []

    with os.scandir(dir) as it:
        for entry in it:
            if entry.is_dir():
                if entry.name.startswith('data_collection_'):
                    data_folders.append(dir + '/' + entry.name)
                else:
                    subsearch = searchDir(entry.path)
                    if subsearch:
                        data_folders.append(subsearch)

    data_folders.sort()
    return data_folders

def getStdDevs(data):
    stdDevs = [[], []]

    for dir in data:
        t, i, v = readLemboxData(dir + '/lembox_data.csv')
        sd_i, sd_v = drawStdDev(t, i, v, "", False)

        stdDevs[0].append(sd_i)
        stdDevs[1].append(sd_v)

    return stdDevs

def plotStdDevs(stdDevs):
    n = []

    i = 1
    for dev in stdDevs[0]:
        n.append(i)
        i += 1

    fig, ax = plt.subplots(2,1, sharex=True, constrained_layout=True)
    ax[0].scatter(n, stdDevs[0])
    ax[1].scatter(n, stdDevs[1])
    fig.set_size_inches(15,10)

    plt.show()

    return

def main():

    topDir = selectParent()
    dataFolders = searchDir(topDir)

    stdDevs = getStdDevs(dataFolders)
    plotStdDevs(stdDevs)

if __name__ == '__main__': main()

