# this file contains helper functions to perform computations and store calcualted values

import numpy  as np
import pandas as pd
import sys
import math

def getRollingAvg(arr, avgLen = 1000):
    if np.isnan(arr).any():
        print('Array has NaN')
    
    if avgLen <= 1:
        print('Average window too small: must be larger than 2')
        sys.exit(1)

    if type(arr) != list: arr = arr.tolist()

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

def getRollingStdDev(arr, sd_scale=5000):

    avg_arr = getRollingAvg(arr, sd_scale)
    avg_arr = avg_arr[sd_scale - 1:]

    buffer = [[], []]

    for a in arr[:sd_scale - 1]:
        buffer[0].append(math.pow(a,2))
        buffer[1].append(a)

    s = []
    s.append(sum(buffer[0]))
    s.append(sum(buffer[1]))

    sd = []
    for i, a in enumerate(arr[sd_scale - 1:]):
        buffer[0].append(math.pow(a,2))
        buffer[1].append(a)

        s[0] += buffer[0][-1]
        s[1] += buffer[1][-1]

        sd.append(math.sqrt((s[0] - (2 * avg_arr[i] * s[1]))/sd_scale + math.pow(avg_arr[i],2)))

        s[0] -= buffer[0].pop(0)
        s[1] -= buffer[1].pop(0)

    return sd

def getRollingSkew(arr, sk_scale=5000):

    avg_arr = getRollingAvg(arr, sk_scale)
    avg_arr = avg_arr[sk_scale - 1:]

    sd = getRollingStdDev(arr, sk_scale)

    buffer = [[], [], []]
    for a in arr[:sk_scale - 1]:
        buffer[0].append(math.pow(a,3))
        buffer[1].append(math.pow(a,2))
        buffer[2].append(a)

    s = []
    s.append(sum(buffer[0]))
    s.append(sum(buffer[1]))
    s.append(sum(buffer[2]))

    sk = []
    for i, a in enumerate(arr[sk_scale - 1:]):
        buffer[0].append(math.pow(a,3))
        buffer[1].append(math.pow(a,2))
        buffer[2].append(a)

        s[0] += buffer[0][-1]
        s[1] += buffer[1][-1]
        s[2] += buffer[2][-1]

        sk.append((((s[0] - (3 * avg_arr[i] * s[1]) + (3 * math.pow(avg_arr[i], 2) * s[2]))/sk_scale) - math.pow(avg_arr[i], 3)) / math.pow(sd[i], 3))

        s[0] -= buffer[0].pop(0)
        s[1] -= buffer[1].pop(0)
        s[2] -= buffer[2].pop(0)

    return sk

def getRollingKurtosis(arr, k_scale=5000):

    avg_arr = getRollingAvg(arr, k_scale)
    avg_arr = avg_arr[k_scale - 1:]

    sd = getRollingStdDev(arr, k_scale)

    buffer = [[], [], [], []]
    for a in arr[:k_scale - 1]:
        buffer[0].append(math.pow(a,4))
        buffer[1].append(math.pow(a,3))
        buffer[2].append(math.pow(a,2))
        buffer[3].append(a)

    s = []
    s.append(sum(buffer[0]))
    s.append(sum(buffer[1]))
    s.append(sum(buffer[2]))    
    s.append(sum(buffer[3]))

    k = []
    for i, a in enumerate(arr[k_scale - 1:]):
        buffer[0].append(math.pow(a,4))
        buffer[1].append(math.pow(a,3))
        buffer[2].append(math.pow(a,2))
        buffer[3].append(a)

        s[0] += buffer[0][-1]
        s[1] += buffer[1][-1]
        s[2] += buffer[2][-1]
        s[3] += buffer[3][-1]

        k.append((((s[0] - (4 * avg_arr[i] * s[1]) + (6 * math.pow(avg_arr[i], 2) * s[2]) - (4 * math.pow(avg_arr[i], 3) * s[3]))/k_scale) + math.pow(avg_arr[i], 4)) / math.pow(sd[i], 4))

        s[0] -= buffer[0].pop(0)
        s[1] -= buffer[1].pop(0)
        s[2] -= buffer[2].pop(0)
        s[3] -= buffer[3].pop(0)


    return k

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

print(getRollingStdDev([500, 2, 100, 450, 600], 5))
print(getRollingSkew([500, 2, 100, 450, 600], 5))
print(getRollingKurtosis([500, 2, 100, 450, 600], 5))