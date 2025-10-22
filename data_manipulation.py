# this file contains helper functions to perform computations and store calcualted values

import numpy  as np
import pandas as pd
import sys
import math

def getRollingAvg(arr, avgLen = 1000):
    if np.isnan(arr).any():
        print('Array has NaN')
    
    if avgLen <= 2:
        print('Average window too small: must be larger than 2')
        sys.exit(1)

    arr = arr.tolist()

    avg = []
    for i in range(avgLen-1):
        avg.append(float('NaN'))

    buffer = arr[:avgLen - 1]
    
    for r in range(len(buffer)):
        if math.isnan(buffer[r]): buffer[r] = buffer[r-1]
    
    s = sum(buffer)

    for v in range(len(arr[avgLen-1:])):
        v = v+avgLen - 1

        buffer.append(arr[v])
        if math.isnan(buffer[-1]):
            buffer[-1] = buffer[-2]
        s += buffer[-1]

        avg.append(s/avgLen)    
        s -= buffer.pop(0)

    return avg

# takes an array and a limit value and returns the start:stop indices that bound  (array's value) > testLimit
def getStartStop(testVal, testLimit = 1):

    startTime = 0
    for t, v in enumerate(testVal):
        if v > testLimit: 
            startTime = t
            break

    stopTime = 0
    for t, v in enumerate(testVal):
        if t < startTime:
            continue

        if testVal[t - 1] >=  testLimit and v < testLimit:
            stopTime = t

    if stopTime == 0: stopTime = len(testVal)

    return startTime, stopTime

def getStdDev(arr):
    return np.std(arr)

def dfAddColumn(df, arr, id):

    df[id] = arr
    return df

def dfToCsv(df, f):
    df.to_csv(f, index=False)

def dfHasColumn(df, id):

    if id in df.columns: return True
    return False

def csvHasColumn(f, id):

    if id in pd.read_csv(f, nrows=1): return True
    return False