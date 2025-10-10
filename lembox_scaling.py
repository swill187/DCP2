import pandas as pd
import os
import sys
import numpy as np
import datetime

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    # Make paths relative to script directory if it's not absolute
    input_file = os.path.join(script_dir, sys.argv[1]) if not os.path.isabs(sys.argv[1]) else sys.argv[1]
else:
    input_file = os.path.join(script_dir, 'lembox_data.csv')

print(f"Reading and updating file: {input_file}")

col_types = {
    'Sample': np.int32,
    'PerfTime(s)': np.float64,
    'Timestamp': str,
    'VoltageRaw': str,
    'Voltage(V)': np.float64,
    'CurrentRaw': str,
    'Current(A)': np.float64,
}

# Read, scale, and update the data in place

# added explicit dtype definitions to prevent dtypeWarning message. skipfooter avoids type error caused by debugging messages appended to data. python engine is required to use the skipfooter option.
df = pd.read_csv(input_file, dtype=col_types, skipfooter=2, engine='python')
df['Scaled_Voltage(V)'] = df['Voltage(V)'] * 10
df['Scaled_Current(A)'] = df['Current(A)'] * 100

# Save back to the same file
df.to_csv(input_file, index=False)
print(f"Scaling complete. Original file updated: {input_file}")