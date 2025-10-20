import pandas as pd
import sys
from tkinter import filedialog
from lembox_visualization import getLemboxData, getTimeData
from position import readRSI, plotPosValColormap
from data_manipulation import dfToCsv
import os
import matplotlib.pyplot as plt

def alignData(dir, lem, rsi, forceDataUpdate=False):
    print('         Aligning data...')

    if not os.access(dir +'/aligned_data.csv', os.R_OK) or forceDataUpdate:

        aligned_data = ()
        for i in range(len(rsi) - 1): aligned_data += ([],)

        rsi_index = 0
        for t in lem[0]:
            while t > rsi[-1][rsi_index] and rsi_index < len(rsi[-1]) - 1: rsi_index += 1

            for i in range(len(rsi) - 1):
                aligned_data[i].append(rsi[i][rsi_index])

        df = pd.DataFrame({'time':lem[0], 'Current(A)': lem[1], 'Avg_Current(A)': lem[2], 
                            'Voltage(V)': lem[3], 'Avg_Voltage(V)': lem[4], 'Pos_x(mm)': aligned_data[0], 
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

    startTime += 40000 ; stopTime -= 40000
    lem = (lem_time, curr, avgI, volt, avgV)

    pos, vel, rsi_time = readRSI(dir + '/robot_data.csv', True)
    rsi = (pos[0], pos[1], pos[2], vel[0], vel[1], vel[2], vel[3], rsi_time)

    df = alignData(dir, lem, rsi)

    plotPosValColormap((df['Pos_x(mm)'][startTime:startTime + int(5.5 * 20000)], df['Pos_y(mm)'][startTime:startTime + int(5.5 * 20000)], df['Pos_z(mm)'][startTime:startTime + int(5.5 * 20000)]), df['Avg_Current(A)'][startTime:startTime + int(5.5 * 20000)], 'Rolling Average Current (A)', 'Current as a function of position', 75)
    plt.savefig(dir + '/visualizations/current_3d_short.png', bbox_inches='tight')
    plotPosValColormap((df['Pos_x(mm)'][startTime:startTime + int(5.5 * 20000)], df['Pos_y(mm)'][startTime:startTime + int(5.5 * 20000)], df['Pos_z(mm)'][startTime:startTime + int(5.5 * 20000)]), df['Avg_Voltage(V)'][startTime:startTime + int(5.5 * 20000)], 'Rolling Average Voltage (V)', 'Voltage as a function of position', 14)
    plt.savefig(dir + '/visualizations/voltage_3d_short.png', bbox_inches='tight')

if __name__ == '__main__': main()