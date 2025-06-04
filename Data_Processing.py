import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

def select_folder():
    """Open a folder selection dialog and return the selected path"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(
        title='Select Data Collection Folder',
        initialdir=os.path.expanduser('~')  # Start in user's home directory
    )
    return folder_path

def process_data_folder(folder_path):
    """Process different types of data files in the given folder using appropriate scripts."""
    folder = Path(folder_path)
    script_dir = Path(__file__).parent
    
    # Dictionary mapping file patterns to their processing scripts
    processing_rules = {
        'microphone_data.csv': 'audio_conversion.py',
        'robot_data.txt': 'robotdata_parsing.py',
        'lembox_data.csv': 'lembox_scaling.py'
    }
    
    # Process regular files
    for file_path in folder.glob('*'):
        if file_path.is_file():
            file_name = file_path.name
            if file_name in processing_rules:
                script_name = processing_rules[file_name]
                script_path = script_dir / script_name
                
                if not script_path.exists():
                    print(f"Processing script not found: {script_path}")
                    continue
                
                print(f"\nProcessing {file_path} with {script_name}")
                try:
                    if script_name == 'robotdata_parsing.py':
                        # Special handling for robot data to specify output path
                        output_path = file_path.with_suffix('.csv')
                        subprocess.run([sys.executable, str(script_path), 
                                     str(file_path), str(output_path)], check=True)
                    else:
                        subprocess.run([sys.executable, str(script_path), 
                                     str(file_path)], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error running {script_name}: {e}")
    
    # Check for FLIR folder
    flir_folder = folder / 'FLIR'
    if flir_folder.is_dir():
        flir_script = script_dir / 'create_flirvideo.py'
        if not flir_script.exists():
            print(f"FLIR processing script not found: {flir_script}")
            return
            
        print("\nProcessing FLIR folder...")
        try:
            output_video = folder / 'FLIR.mp4'
            output_frames = folder / 'FLIR_Frames'
            subprocess.run([sys.executable, str(flir_script), 
                          str(flir_folder),
                          str(output_video),
                          str(output_frames)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing FLIR folder: {e}")

def main():
    print("Please select the data collection folder...")
    folder_path = select_folder()
    
    if not folder_path:
        print("No folder selected. Exiting...")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)
    
    print(f"\nProcessing folder: {folder_path}")
    process_data_folder(folder_path)

if __name__ == "__main__":
    main()