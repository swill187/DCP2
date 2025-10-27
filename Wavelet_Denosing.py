import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from tkinter             import filedialog
import pywt

def DWT(f):
    print('...DWT of Amplitude Data')
    df = pd.read_csv(f)
    Amp = df['Amplitude']
    Time = df['time']
    print(Amp)
    DWTcoeffs = pywt.wavedec(Amp, 'db3',)
    DWTcoeffs[-1] = np.zeros_like(DWTcoeffs[-1]) # rough version of denosing which sets the last two detal coeffs. to zero
    DWTcoeffs[-2] = np.zeros_like(DWTcoeffs[-2])
  
   
    print(DWTcoeffs)
    filtered_data_dwt=pywt.waverec(DWTcoeffs,'db3',mode='symmetric',axis=-1)
    print(filtered_data_dwt)

    sample_rate = 48000
    

    start_index = int(8*sample_rate)
    end_index = int(8.01*sample_rate)


    plt.figure(figsize=(15,6))
    plt.plot(Time[start_index:end_index],Amp[start_index:end_index],color='red')
    plt.plot(Time[start_index:end_index],filtered_data_dwt[start_index:end_index], markerfacecolor='none',color='black')
    plt.legend(['Real Data', 'Denoised Data'], loc='best')
    plt.show()
    return

def main():
    if len(sys.argv) != 2:
        csv_file = filedialog.askopenfilename()
    else:
        csv_file = sys.argv[1]
    DWT(csv_file)

if __name__ == "__main__":
    main()