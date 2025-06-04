# DCP2
Development Cell Post Processing (DCP2) program to be used on data collected using the Development Cell Data Collection (DC2) program.

# Run these commands in the terminal
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python Data_Processing.py

# Data_Processing.py
The main function. It will prompt the user to select a data folder from an experiment. Then, it goes through the folder, identifies what data files are in it and executes functions to further process the data to more usable forms. The other Python scripts listed here are modules with functions to process different data types.
# audio_conversion.py
Converts audio recorded in CSV format to WAV format to enable listening

# lembox_scaling.py
Multiplies the voltage and current readings collected from the Miller LEM Box by 10 and 100 respectively to scale them to their true values

# robotdata_parsing.py
Takes robot messages recorded in text document with XML format and parses them, writing them to a CSV file

# create_flirvideo
Take folder of FLIR data saved in numpy format and creates color mapped image frames and a video for viewing

# create_xirisvideo.py
....