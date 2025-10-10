import matplotlib.pyplot as plt
import matplotlib        as mpl
import sys
import os
import pandas            as pd
import numpy             as np
import librosa
import math

sample_rate = 20000 #hz

def readLemboxData(f):
    print('         Reading LEMBOX Data...')

    df = pd.read_csv(f)

    count = df['Sample'].to_numpy().astype(float)
    curr = df['Scaled_Current(A)'].to_numpy()
    volt = df['Scaled_Voltage(V)'].to_numpy()

    time = count
    for r in range(len(time)):
        time[r] = time[r]/float(sample_rate)

    return  time, curr, volt

def getLemboxAvgs(rawV, rawI, rawT, avgLen = 4096):
    if np.isnan(rawV).any():
        print('rawV has NaN')
        
    if np.isnan(rawI).any():
        print('rawI has NaN')
        
    if np.isnan(rawT).any():
        print('rawT has NaN')
    
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
    
    for r in range(len(vBuffer)):
        if math.isnan(vBuffer[r]):
            print('vBuffer init has NaN')
            vBuffer[r] = vBuffer[r-1]
    
    s = sum(vBuffer)

    for v in range(len(avgT)):
        v = v+avgLen - 1

        vBuffer.append(rawV[v])
        if math.isnan(vBuffer[-1]):
            vBuffer[-1] = vBuffer[-2]
        s += vBuffer[-1]

        avgV.append(s/avgLen)    
        s -= vBuffer.pop(0)

    iBuffer = rawI[0: avgLen - 1]
    for r in range(len(iBuffer)):
        if math.isnan(iBuffer[r]):
            print('iBuffer init has NaN')
            iBuffer[r] = iBuffer[r-1]
            
            
    s = sum(iBuffer)

    for i in range(len(avgT)):
        i = i+avgLen - 1

        iBuffer.append(rawI[i])
        if math.isnan(iBuffer[-1]):
            iBuffer[-1] = iBuffer[-2]
        s += iBuffer[-1]

        avgI.append(s/avgLen)
        s -= iBuffer.pop(0)

    t_avg = rawT[10000 + avgLen] - rawT[10000]        # compute time length of rolling average

    return t_avg, avgV, avgI, avgT

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

    print('StdDev V: ' + str(np.std(v)))
    print('StdDev I: ' + str(np.std(i)))

    return np.std(i), np.std(v)

def drawLemboxVis(f, **kwargs):

    startup = False

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
            startup = True

    t, i, v = readLemboxData(f)

    t_scale, avgV, avgI, avgT = getLemboxAvgs(v, i, t, n)
    startTime, stopTime = getTimeData(avgV, avgT)
    
    t_scale = f"{t_scale:.5f}"

    startTime -= 2*sample_rate
    stopTime += 2*sample_rate
    
    if startTime < 0:
        startTime = 0
    if stopTime > len(avgV):
        stopTime = len(avgV)

    startNonAvg = t.tolist().index(avgT[startTime])
    stopNonAvg = startNonAvg + (stopTime - startTime)

    t = t[startNonAvg:stopNonAvg]
    i = i[startNonAvg:stopNonAvg]
    v = v[startNonAvg:stopNonAvg]
    avgV = avgV[startTime:stopTime]
    avgI = avgI[startTime:stopTime]
    avgT = avgT[startTime:stopTime]

    #drawAudioFFT(dir)

    dir = os.path.split(f)[0]

    print('         Drawing LEMBOX vis...')

    begin = 5* sample_rate
    l = int(10 * sample_rate)
    shortscaleFFT(v[begin:(begin+l)], i[begin:(begin+l)], f, sample_rate)
    
    plt.style.use('_mpl-gallery')
    mpl.rcParams['lines.markersize'] = pt_sz*2
    mpl.rcParams['figure.constrained_layout.use'] = True

    drawStdDev(t, i, v, dir)

    fig, ax = plt.subplots(2,2, sharex=True)

    if startup:
        plot_range_start = int(1.95*sample_rate)
        plot_range_stop = int(2*sample_rate) + int(0.5*sample_rate) + int(0.1*sample_rate)
    else:
        plot_range_start = 0
        plot_range_stop = -1

    ax[0,0].scatter(t[plot_range_start:plot_range_stop], v[plot_range_start:plot_range_stop])
    ax[0,0].set_title('Voltage')
    ax[0,0].set_ylabel('Voltage (V)')

    ax[1,0].scatter(avgT[plot_range_start:plot_range_stop], avgV[plot_range_start:plot_range_stop])
    ax[1,0].set_title('Rolling Voltage Average Over ' + t_scale + ' Seconds')
    ax[1,0].set_ylabel('Average Voltage (V)')
    ax[1,0].set_xlabel('Time (s)')

    ax[0,1].scatter(t[plot_range_start:plot_range_stop], i[plot_range_start:plot_range_stop])
    ax[0,1].set_title('Current')
    ax[0,1].set_ylabel('Current (A)')

    ax[1,1].scatter(avgT[plot_range_start:plot_range_stop], avgI[plot_range_start:plot_range_stop])
    ax[1,1].set_title('Rolling Current Average Over ' + t_scale + ' Seconds')
    ax[1,1].set_ylabel('Average Current (A)')
    ax[1,1].set_xlabel('Time (s)')

    fig.set_size_inches(30,10)
    plt.savefig(dir + '/visualizations/lembox.png')
    
    return

def getTimeData(avgV, avgT):
    startTime = 0
    while True:
        if avgV[startTime] > 1:
            break
        startTime += 1

    stopTime = 0
    while True:
        if stopTime < startTime:
            stopTime += 1
            continue
        elif avgV[stopTime] < 1 or stopTime >= len(avgV) - 1:
            break
        stopTime += 1

    return startTime, stopTime

def shortscaleFFT(v, i, f, rate):
    vArr = np.array(v)
    iArr = np.array(i)

    dir = os.path.split(f)[0]

    vDFT = np.fft.rfft(vArr)
    iDFT = np.fft.rfft(iArr)

    freq = np.fft.rfftfreq(len(v), 1/rate)

    #print(np.size(DFT))
    #print(np.size(freq))

    #print(DFT)
    #print(freq)

    #mpl.rcParams['lines.markersize'] = 0.05*2
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots(2,1)
    ax[0].plot(freq[1:int(len(freq)/10)], np.abs(iDFT[1:int(len(freq)/10)]), 'r', alpha=.85, label='Current FFT')
    ax[1].plot(freq[1:int(len(freq)/10)], np.abs(vDFT[1:int(len(freq)/10)]), 'b', alpha = .85, label='Voltage FFT')
    ax[1].set_xlabel('Frequency (Hz)')
    ax[1].set_ylabel('Voltage FFT Amplitude')
    ax[0].set_ylabel('Current FFT Amplitude')
    fig.set_size_inches(15,20)
    plt.savefig(dir + '/visualizations/lembox_fft.png')
    
    return

"""
def drawAudioFFT (dir):
    start = 1929902
    stop = 4342281


    csv_filename = dir + '/microphone_data.csv'
    df = pd.read_csv(csv_filename, skiprows=1, low_memory=False)
    array = df['Amplitude'].to_numpy()
    sr = librosa.get_samplerate(dir + '/microphone_data.wav')

    timescale = .5
    DFT1 = np.fft.rfft(array[start:int(start+(timescale*sr))])
    DFT2 = np.fft.rfft(array[int(stop-(timescale*sr)):stop])
    freq = np.fft.rfftfreq(len(array[start:int(start+(timescale*sr))]), 1/sr)

    fig,ax = plt.subplots(2,1, layout='constrained')
    fig.set_size_inches(15,20)
    ax[0].plot(freq[5:-1], np.abs(DFT1)[5:-1])
    ax[1].plot(freq[5:-1], np.abs(DFT2)[5:-1])
    ax[1].set_xlabel('Frequency (Hz)')
    ax[1].set_ylabel('Audio Data FFT Amplitude (Without Shielding Gas)')
    ax[0].set_ylabel('Audio Data FFT Amplitude (With Shielding Gas)')

    plt.savefig(dir +'/visualizations/audio_fft.png')

    return
    """
    

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