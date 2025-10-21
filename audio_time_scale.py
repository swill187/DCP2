import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

def mic_time(csv_filename, aligned_filename, sample_rate=48000):
    try:
        # Load CSV, skipping header row if needed
        df = pd.read_csv(csv_filename, skiprows=1)

        print("First 5 rows:")
        print(df.head())

        print("\nColumn names:")
        print(df.columns)

        # Generate time scale
        num_samples = len(df)
        time_end = num_samples / sample_rate
        print(f"\nTotal samples: {num_samples}")
        print(f"Duration (s): {time_end:.2f}")

        df['Time'] = np.arange(num_samples) / sample_rate

        # Check if 'Amplitude' column exists
        if 'Amplitude' not in df.columns:
            raise ValueError("Column 'Amplitude' not found in CSV.")

        columns_to_save = ['Time', 'Amplitude']
        new_df = df[columns_to_save]

        # Save new CSV
        new_df.to_csv(aligned_filename, index=False)
        print(f"\nSaved to: {aligned_filename}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv>")
        sys.exit(1)

    csv_filename = sys.argv[1]

    # Generate output filename in same directory
    output_name = os.path.splitext(csv_filename)[0] + '_aligned.csv'

    mic_time(csv_filename, aligned_filename=output_name, sample_rate=48000)

if __name__ == "__main__":
    main()
