import matplotlib.pyplot as plt
import matplotlib        as mpl
import sys
import os
import pandas            as pd
import numpy             as np

def readLemboxData(f):
    print('         Reading LEMBOX Data...')

    df = pd.read_csv(f, skipfooter=1, engine='python')

    time = df['PerfTime(s)'].to_numpy()
    curr = df['Scaled_Current(A)'].to_numpy()
    volt = df['Scaled_Voltage(V)'].to_numpy()

    return  time, curr, volt

def getLemboxAvgs(rawV, rawI, rawT, avgLen = 4096):
    if avgLen <= 2:
        print('Average window too small: must be larger than 2')
        sys.exit(1)


    print('         Calculating LEMBOX avgs...')

    rawV = rawV.tolist()
    rawI = rawI.tolist()
    rawT = rawT.tolist()

    avgV = []
    avgI = []
    avgT = rawT[avgLen - 1:]

    vBuffer = rawV[0: avgLen - 1]
    s = sum(vBuffer)

    for v in range(len(avgT)):
        v = v+avgLen - 1

        vBuffer.append(rawV[v])
        s += rawV[v]

        avgV.append(s/avgLen)
        s -= vBuffer.pop(0)

    iBuffer = rawI[0: avgLen - 1]
    s = sum(iBuffer)

    for i in range(len(avgT)):
        i = i+avgLen - 1

        iBuffer.append(rawI[i])
        s += rawI[i]

        avgI.append(s/avgLen)
        s -= iBuffer.pop(0)

    t_avg = rawT[50*avgLen] - rawT[49*avgLen]        # compute time length of rolling average

    return t_avg, avgV, avgI, avgT

def drawLemboxVis(f, pt_sz = 0.05):
    t, i, v = readLemboxData(f)
    t_scale, avgV, avgI, avgT = getLemboxAvgs(v, i, t, 1000)
    
    t_scale = f"{t_scale:.5f}"

    print('         drawing LEMBOX vis...')

    dir = os.path.split(f)[0]

    plt.style.use('_mpl-gallery')
    mpl.rcParams['lines.markersize'] = pt_sz*2
    mpl.rcParams['figure.constrained_layout.use'] = True

    fig, ax = plt.subplots(2,2)

    ax[0,0].scatter(t, v)
    ax[0,0].set_title('Voltage')
    ax[0,0].set_ylabel('Voltage (V)')

    ax[1,0].scatter(avgT, avgV)
    ax[1,0].set_title('Rolling Voltage Average Over ' + t_scale + ' Seconds')
    ax[1,0].set_ylabel('Average Voltage (V)')
    ax[1,0].set_xlabel('Time (s)')

    ax[0,1].scatter(t, i)
    ax[0,1].set_title('Current')
    ax[0,1].set_ylabel('Current (A)')

    ax[1,1].scatter(avgT, avgI)
    ax[1,1].set_title('Rolling Current Average Over ' + t_scale + ' Seconds')
    ax[1,1].set_ylabel('Average Current (A)')
    ax[1,1].set_xlabel('Time (s)')

    fig.set_size_inches(30,10)
    plt.savefig(dir + '/visualizations/lembox.png')


    return

def main():
    if len(sys.argv) != 2:
        print('Usage: python lembox_visualization.py <lembox_csv_file>')
        sys.exit(1)

    csv_file = sys.argv[1]
    dir = os.path.split(csv_file)[0]

    try:
        os.mkdir(dir + '/visualizations')
    except FileExistsError:
        pass

    print('Generating LEMBOX data visualizations...')
    drawLemboxVis(csv_file)
    print('LEMBOX visualization complete')
    return

if __name__ == "__main__":
    main()