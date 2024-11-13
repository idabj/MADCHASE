import os
import glob
import logging
from dataprocessing import DataPlotter
import re
import json
import numpy as np

logging.basicConfig(
    format="{asctime}-{levelname}-{message}",
    style = "{",
    datefmt = "%Y-%m-%d %H:%M",
    level=logging.INFO,
)

def find_measurement_folders(base_folder):
    measurement_pattern = os.path.join(base_folder, "measurement_*_*")
    measurement_folders = glob.glob(measurement_pattern)
    
    return measurement_folders

def extract_measurement_number(filename):
    pattern = r"data_measurement_.*_(\d+)\.json"
    match = re.search(pattern, filename)

    if match: 
        return int(match.group(1))
    else:
        logging.warning("Could not find measurement number!")
        return None
    
    
def change_plots(measurement_name):
    measurement_folders = find_measurement_folders(measurement_name)
    
    for measurement_folder in measurement_folders:
        folder_path_plot = measurement_folder
        file_paths_json = glob.glob(os.path.join(measurement_folder, "data_measurement_*_*.json"))
        
        for file_path_json in file_paths_json:
            logging.info("JSON path: %s" % file_path_json)
            measurement_number = extract_measurement_number(file_path_json)
            if measurement_number is None:
                continue
            
            logging.info("Measurement number %d" % measurement_number)
            plotter = DataPlotter(file_path_json, folder_path_plot, measurement_number)

            plotter.plot_data()

            
pattern = os.path.join("measurements/", "*/")
measurement_folders = glob.glob(pattern)

# Update plots in all measurement folders
for measurement_name in measurement_folders:
    logging.info("Measurement name: %s" % measurement_name)
    change_plots(measurement_name)
