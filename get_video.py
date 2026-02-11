import cv2 as cv
import os
from tkinter import filedialog
import numpy as np

def getFrames(f):
    print('Collecting Frames...')

    frames = []
    with os.scandir(f) as it:   
        for entry in it:
            if entry.is_file() and not entry.name.startswith('FLIR_Variables') and not entry.name.startswith('.index'):
                frames.append(cv.imread(entry.path))
            elif entry.is_dir():
                fr = getFrames(entry.path)
                for frame in fr:
                    frames.append(frame)

    return frames

def buildVideo(f, frames):
    print('Constructing Video...')

    fourcc = cv.VideoWriter_fourcc(*'mp4v')

    print(frames[-1].shape[0])
    print(frames[-1].shape[1])
    out = cv.VideoWriter(os.path.split(f)[0] + '/output.mp4', fourcc, 30, (frames[-1].shape[1], frames[-1].shape[0]))

    for frame in frames:
        out.write(frame)

    out.release()
    cv.destroyAllWindows()
    return

def main():
    parent = filedialog.askdirectory()

    vid = getFrames(parent)

    buildVideo(parent, vid)

    return

if __name__ == '__main__': main()