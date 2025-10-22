import matplotlib.pyplot as plt
import matplotlib        as mpl
import sys
import os
import pandas            as pd
import numpy             as np

from data_manipulation import getRollingAvg, getStartStop, dfHasColumn, dfAddColumn, dfToCsv

sample_rate = 20000 #hz

def getLemboxData(f, n = 1000, forceDataUpdate=False):
    print('         Reading LEMBOX Data...')

    df = pd.read_csv(f)

    curr = df['Scaled_Current(A)'].to_numpy()
    volt = df['Scaled_Voltage(V)'].to_numpy()

    if not dfHasColumn(df, 'Avg_Voltage(V)') or forceDataUpdate or n==200:
        avgV =  getRollingAvg(volt, n)
        avgI = getRollingAvg(curr, n)

        count = df['Sample'].to_numpy().astype(float)
        time = count
        for r in range(len(time)):
            time[r] = time[r]/float(sample_rate)

        dfAddColumn(df, avgV, 'Avg_Voltage(V)')
        dfAddColumn(df, avgI, 'Avg_Current(A)')
        dfAddColumn(df, time, 'Interpolated_Time(s)')

        if n != 200:
            dfToCsv(df, f)
    else:
        avgV = df['Avg_Voltage(V)']
        avgI = df['Avg_Current(A)']
        time = df['Interpolated_Time(s)']

    return  time, df['Scaled_Current(A)'], df['Scaled_Voltage(V)'], avgI, avgV

def drawStdDev(t, i, v, d, draw=True):
    sd_scale = 20000

    if draw:
        sd_i = []
        sd_v = []
        for a in range(len(t[sd_scale - 1:])):
            sd_i.append(np.std(i[a: a + sd_scale - 1]))
            sd_v.append(np.std(v[a: a + sd_scale - 1]))

        fig, ax = plt.subplots(2,1, sharex=True)
        ax[0].scatter(t[sd_scale - 1:], sd_v)
        ax[0].set_ylabel('Voltage Std Dev')
        ax[1].scatter(t[sd_scale - 1:], sd_i)
        ax[1].set_ylabel('Current Std Dev')
        ax[1].set_xlabel('Time (s)')
        fig.set_size_inches(15,10)

        plt.savefig(d + '/visualizations/stddev.png')

    sd_i = np.nanstd(i)
    sd_v = np.nanstd(v)
    print('StdDev I: ' + str(sd_i))
    print('StdDev V: ' + str(sd_v))

    return sd_i, sd_v

def plotLemboxData(v, t, i, avgV, avgI, t_scale, file, p_start, p_stop):
        fig, ax = plt.subplots(2,2, sharex=True)

        ax[0,0].scatter(t[p_start:p_stop], v[p_start:p_stop])
        ax[0,0].set_title('Voltage')
        ax[0,0].set_ylabel('Voltage (V)')

        ax[1,0].scatter(t[p_start:p_stop], avgV[p_start:p_stop])
        ax[1,0].set_title('Rolling Voltage Average Over ' + t_scale + ' Seconds')
        ax[1,0].set_ylabel('Average Voltage (V)')
        ax[1,0].set_xlabel('Time (s)')

        ax[0,1].scatter(t[p_start:p_stop], i[p_start:p_stop])
        ax[0,1].set_title('Current')
        ax[0,1].set_ylabel('Current (A)')

        ax[1,1].scatter(t[p_start:p_stop], avgI[p_start:p_stop])
        ax[1,1].set_title('Rolling Current Average Over ' + t_scale + ' Seconds')
        ax[1,1].set_ylabel('Average Current (A)')
        ax[1,1].set_xlabel('Time (s)')

        fig.set_size_inches(30,10)
        plt.savefig(file)

        return

def drawLemboxVis(f, **kwargs):

    dir = os.path.split(f)[0]
    file = dir + '/visualizations/lembox.png'

    startup = False
    p_start = 0
    p_stop = -1

    if 'pt_sz' in kwargs:
        pt_sz = kwargs['pt_sz']
    else:
        pt_sz = 0.005

    if 'avg_len' in kwargs:
        n = kwargs['avg_len']
    else:
        n = 1000

    # this should call a second call to drawLemboxVis
    if 'startup' in kwargs:
        if kwargs['startup'] == True:
            pt_sz = 0.25
            n = 200
            file = dir + '/visualizations/shortscale_lembox.png'
            startup = True
            #p_start = int(1.95*sample_rate)
            #p_stop = int(2*sample_rate) + int(0.5*sample_rate) + int(0.1*sample_rate)
            p_start = int(10*sample_rate)
            p_stop = int(10*sample_rate) + int(0.6*sample_rate)

    t, i, v, avgI, avgV = getLemboxData(f, n)

    t_scale = t[int(len(t)/2) + n] - t[int(len(t)/2)]        # compute time length of rolling average
    t_scale = f"{t_scale:.5f}"

    startTime, stopTime = getStartStop(avgV, 1)

    startTime -= 2*sample_rate      # set observed window to welding time +- 2 seconds
    stopTime += 2*sample_rate
    if startTime < 0:
        startTime = 0
    if stopTime > len(avgV):
        stopTime = len(avgV)

    t = t[startTime:stopTime]
    i = i[startTime:stopTime]
    v = v[startTime:stopTime]
    avgV = avgV[startTime:stopTime]
    avgI = avgI[startTime:stopTime]

    print('         Drawing LEMBOX vis...')

    plt.style.use('_mpl-gallery')
    mpl.rcParams['lines.markersize'] = pt_sz*2
    mpl.rcParams['figure.constrained_layout.use'] = True

    begin = 5* sample_rate
    l = int(10 * sample_rate)
    shortscaleFFT(v[begin:(begin+l)], i[begin:(begin+l)], f, sample_rate)

    #drawStdDev(t, i, v, dir)
    plotLemboxData(v, t, i, avgV, avgI, t_scale, file, p_start, p_stop)
    
    return

def shortscaleFFT(v, i, f, rate):
    vArr = np.array(v)
    iArr = np.array(i)

    dir = os.path.split(f)[0]

    vDFT = np.fft.rfft(vArr)
    iDFT = np.fft.rfft(iArr)

    freq = np.fft.rfftfreq(len(v), 1/rate)

    #mpl.rcParams['lines.markersize'] = 0.05*2
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots(2,1)
    ax[0].plot(freq[1:int(len(freq)/50)], np.abs(iDFT[1:int(len(freq)/50)]), 'r', alpha=.85, label='Current FFT')
    ax[1].plot(freq[1:int(len(freq)/50)], np.abs(vDFT[1:int(len(freq)/50)]), 'b', alpha = .85, label='Voltage FFT')
    ax[1].set_xlabel('Frequency (Hz)')
    ax[1].set_ylabel('Voltage FFT Amplitude')
    ax[0].set_ylabel('Current FFT Amplitude')
    fig.set_size_inches(15,20)
    plt.savefig(dir + '/visualizations/lembox_fft.png')
    
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
    drawLemboxVis(csv_file, startup=False)
    print('LEMBOX visualization complete')
    return

if __name__ == "__main__":
    main()