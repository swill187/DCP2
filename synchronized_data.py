import pandas as pd
import sys
from tkinter import filedialog
from lembox_visualization import getLemboxData, getTimeData
from position import readRSI, plotPosValColormap
from data_manipulation import dfToCsv
from audio_time_scale import mic_time
import os
import matplotlib.pyplot as plt

def alignData(dir, lem, rsi, mic, forceDataUpdate=False):
    print('         Aligning data...')

    if not os.access(dir +'/aligned_data.csv', os.R_OK) or forceDataUpdate:

        aligned_data = ()
        for i in range(len(rsi) - 1): aligned_data += ([],)

        rsi_index = 0
        for t in mic[0]:
            while t > rsi[-1][rsi_index] and rsi_index < len(rsi[-1]) - 1: rsi_index += 1

            for i in range(len(rsi) - 1):
                aligned_data[i].append(rsi[i][rsi_index])
        
        aligned_data_lem = ()
        for j in range(len(lem)): aligned_data_lem += ([],)

        lem_index = 0 
        for l in mic[0]:
            while l > lem[0][lem_index] and lem_index < len(lem[0]) - 1: lem_index += 1

            for j in range(len(lem)):
                aligned_data_lem[j].append(lem[j][lem_index])

    
        df = pd.DataFrame({'time':mic[0], 'Amplitude':mic[1], 'Current(A)': aligned_data_lem[1], 'Avg_Current(A)': aligned_data_lem[2], 
                            'Voltage(V)': aligned_data_lem[3], 'Avg_Voltage(V)': aligned_data_lem[4], 'Pos_x(mm)': aligned_data[0], 
                            'Pos_y(mm)': aligned_data[1], 'Pos_z(mm)': aligned_data[2], 'Vel_x(mm/s)': aligned_data[3],
                            'Vel_y(mm/s)': aligned_data[4], 'Vel_z(mm/s)': aligned_data[5], 'Vel_Comb(mm/s)': aligned_data[6]})
       
        dfToCsv(df, dir + '/aligned_data.csv')

    else: df = pd.read_csv(dir + '/aligned_data.csv')

    return df

def main():
    if len(sys.argv) != 2:
        dir = filedialog.askdirectory()
    else:
        dir = sys.argv[1]

    lem_time, curr, volt, avgI, avgV = getLemboxData(dir + '/lembox_data.csv')
    startTime, stopTime = getTimeData(avgV, lem_time, dir)

    startTime += 80000 ; stopTime -= 80000
    lem = (lem_time, curr, avgI, volt, avgV)

    pos, vel, rsi_time = readRSI(dir + '/robot_data.csv', True)
    rsi = (pos[0], pos[1], pos[2], vel[0], vel[1], vel[2], vel[3], rsi_time)
    
    mic_t, mic_A = mic_time(dir + '/microphone_data.csv', dir + '/microphone_data_aligned.csv', sample_rate = 48000)
    mic = (mic_t,mic_A)
    

    df = alignData(dir, lem, rsi, mic)
    print(df)
    plotPosValColormap((df['Pos_x(mm)'], df['Pos_y(mm)'], df['Pos_z(mm)']), df['Avg_Current(A)'], 'Rolling Average Current (A)', 'Current as a function of position')
  
    plotPosValColormap((df['Pos_x(mm)'][:stopTime], df['Pos_y(mm)'][:stopTime], df['Pos_z(mm)'][:stopTime]), df['Avg_Voltage(V)'][:stopTime], 'Rolling Average Voltage (V)', 'Voltage as a function of position')
    
    plotPosValColormap((df['Pos_x(mm)'], df['Pos_y(mm)'], df['Pos_z(mm)']), abs(df['Amplitude']), 'Amplitude', 'Amplitude as a function of position')
    plt.show()
    plt.close()
if __name__ == '__main__': main()