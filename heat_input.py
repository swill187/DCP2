import sys
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import math

plt.rcParams['lines.markersize'] = 0.005
lem_rate = 20000 # Hz
scale = 5000           # num data points used in calculation of velocity. Small numbers produce very large velocities, or zero velocities (resolution of position data)

def get_pos_lem(d):

    lem_dat = pd.read_csv(d + '/lembox_data.csv')
    rsi_dat = pd.read_csv(d + '/robot_data.csv')
    rsi_len = len(rsi_dat['RelativeTime'])

    t =   []
    pos = [[], [], []]

    # associate RSI position data with LEMBOX timescale
    rsi_index = 0
    for time in lem_dat['Sample']:
        new_time = time/lem_rate
        t.append(new_time)

        while new_time > rsi_dat['RelativeTime'][rsi_index]:
            if rsi_index >= rsi_len - 1:
                break
            rsi_index += 1

        pos[0].append(rsi_dat['RIst_X'][rsi_index])
        pos[1].append(rsi_dat['RIst_Y'][rsi_index])
        pos[2].append(rsi_dat['RIst_Z'][rsi_index])
    
    pos_lem = pd.DataFrame({'time':t, 'Voltage':lem_dat['Scaled_Voltage(V)'], 'Current':lem_dat['Scaled_Current(A)'], 'Pos_x':pos[0], 'Pos_y':pos[1], 'Pos_z':pos[2]})

    return pos_lem

def get_vel(pos_lem, d):
    vel = [[], [], [], []]

    # calculate end affector velocity
    for i in range(len(pos_lem['time']) - scale):
        vel[0].append((pos_lem['Pos_x'][i+scale] - pos_lem['Pos_x'][i])/(pos_lem['time'][i+scale] - pos_lem['time'][i]))
        vel[1].append((pos_lem['Pos_y'][i+scale] - pos_lem['Pos_y'][i])/(pos_lem['time'][i+scale] - pos_lem['time'][i]))
        vel[2].append((pos_lem['Pos_z'][i+scale] - pos_lem['Pos_z'][i])/(pos_lem['time'][i+scale] - pos_lem['time'][i]))
        vel[3].append(math.sqrt(math.pow(vel[0][i],2) + math.pow(vel[1][i],2) + math.pow(vel[2][i],2)))

    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot(pos_lem['time'][:(-1 * scale)],vel[0])
    fig.set_size_inches(15,10)
    plt.savefig(d + '/visualizations/x_velocity.png')

    pos_lem = pd.DataFrame({'time':pos_lem['time'][:-scale], 'Voltage':pos_lem['Voltage'][:-scale], 
                            'Current':pos_lem['Current'][:-scale], 'Pos_x':pos_lem['Pos_x'][:-scale], 
                            'Pos_y':pos_lem['Pos_y'][:-scale], 'Pos_z':pos_lem['Pos_z'][:-scale],
                            'vel_x':vel[0], 'vel_y':vel[1], 'vel_z':vel[2], 'vel_comb':vel[3]})
    
    return pos_lem

def get_heat_input(pos_lem, d):

    # calculate instantaneous heat input
    hi = []
    for i in range(len(pos_lem['time'])):
        if pos_lem['vel_comb'][i] == 0:
            hi.append(pos_lem['Voltage'][i] * pos_lem['Current'][i])
        else:
            hi.append((pos_lem['Voltage'][i] * pos_lem['Current'][i])/ pos_lem['vel_comb'][i])

    avgLen = 10000
    avgHI = []
    HIBuffer = hi[0: avgLen - 1]
    
    s = sum(HIBuffer)

    for i in range(len(hi[avgLen - 1:])):
        i = i+avgLen - 1

        HIBuffer.append(hi[i])
        s += HIBuffer[-1]

        avgHI.append(s/avgLen)    
        s -= HIBuffer.pop(0)


    fig, ax = plt.subplots(3,1, sharex=False, constrained_layout=True)
    ax[0].scatter(pos_lem['time'], hi)
    ax[1].scatter(pos_lem['time'][avgLen - 1:], avgHI)
    ax[2].scatter(pos_lem['time'], pos_lem['vel_comb'])
    ax[0].set_ylim(0,3000)
    ax[1].set_ylim(0,3000)
    fig.set_size_inches(22,10)
    plt.savefig(d + '/visualizations/heat_input.png')

    return pos_lem

def main():
    if len(sys.argv) != 2:
        print('incorrect usage: python \"time_pos_conversion.py [data directory]\"')
        sys.exit(1)

    dir = sys.argv[1]

    print('Converting time-wise LEMBOX data to position-wise data...')
    pos_lem = get_pos_lem(dir)

    print('Computing instantaneous velocity...')
    pos_lem = get_vel(pos_lem, dir)

    print('Computing instantaneous Heat Input...')
    get_heat_input(pos_lem, dir)


if __name__ == '__main__': main()