import matplotlib.pyplot as plt
import pandas as pd
import time
import math
import os
import sys
from data_manipulation import selectFolder
from batch_process     import dataSearch

def getThermocoupleData(d, filename='thermocouple_data.csv'):

    df = pd.read_csv(d + '/' + filename, encoding='cp1252')

    return df

def calibrateThermocoupleData(data):
    gains   = [1.032326969, 1.040573875, 1.052003112, 1.043669245]
    offsets = [-4.295361687, -4.433140888, -5.683631461, -4.651952667]

    cal_data = pd.DataFrame()

    for i in range(4):
        channel = 'Channel ' + str(i) + ' (°C)'
        tcpl = data[channel].tolist()

        for j, t in enumerate(tcpl):
            tcpl[j] = (t*gains[i]) + offsets[i]
        
        cal_data[channel] = pd.Series(tcpl)

    return cal_data



def plotThermocouple(df):
    df_calibrated = calibrateThermocoupleData(df)

    t = df['Timestamp']

    timestamps = []
    for i, timestamp in enumerate(t):
        timestamp_micro = float(timestamp[-6:])/math.pow(10,6)
        timestamp = time.mktime(time.strptime(timestamp[:-7], '%Y-%m-%d %H:%M:%S'))
        timestamp += timestamp_micro

        timestamps.append(timestamp)

    
    startTime = timestamps[0]

    for i, t in enumerate(timestamps):
        timestamps[i] = t - startTime

    temp = []
    cal_temp = []
    for i in range(4):
        channel = 'Channel ' + str(i) + ' (°C)'
        temp.append(df[channel])
        cal_temp.append(df_calibrated[channel])

    fig, ax = plt.subplots(2,1, layout='constrained', sharex=True, sharey=True)

    colors = ['#0d6cbf', '#9d16db','#db2a16', '#16db19']

    for i in range(4):
        ax[0].scatter(timestamps, temp[i], s=2, c=colors[i], label='Channel ' + str(i))
        ax[1].scatter(timestamps, cal_temp[i], s=2, c=colors[i], label='Channel ' + str(i))

    ax[0].set_ylabel('Temperature (°C)')
    ax[0].set_title('Uncalibrated Temperature')
    ax[0].legend(markerscale=3)
    ax[0].grid(True)

    ax[1].set_ylabel('Temperature (°C)')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_title('Calibrated Temperature')
    ax[1].legend(markerscale=3)
    ax[1].grid(True)

    plt.show()

    return

def main():

    if len(sys.argv) == 3:
        dir = sys.argv[1]
        fname = sys.argv[2]

        d = getThermocoupleData(dir, fname)
        plotThermocouple(d)
    else:
        dir = selectFolder()

        if os.path.split(dir)[1].startswith('data_collection'):
            d = getThermocoupleData(dir)
            plotThermocouple(d)
            return
        
        dat = []
        def dataCallback(e):
            d = getThermocoupleData(e.path)
            dat.append(d)
            return

        dataSearch(dir, dataCallback, printFlag=False)
        df = dat.pop()
        while dat:
            df = pd.concat([dat.pop(), df], ignore_index=True)

        plotThermocouple(df)

    return

if __name__ == '__main__': main()