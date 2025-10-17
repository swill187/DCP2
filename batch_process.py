import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog

def selectTopLevel():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(
        title='Select Top-Level Folder to Search',
        initialdir = os.path.expanduser('~')
    )

    return path

def dataSearch(f):
    process_script = os.getcwd() + '/lembox_visualization.py'

    with os.scandir(f) as it:
        for entry in it:
            if entry.is_dir():
                print(entry.name)
                if entry.name.startswith('data_collection_'):
                    print('Found data folder ' + entry.path)
                    subprocess.run([sys.executable, process_script, entry.path + '/lembox_data.csv'], check=True)
                else:
                    dataSearch(entry.path)

def main():
    parent = selectTopLevel()

    dataSearch(parent)

if __name__ == '__main__':
    main()