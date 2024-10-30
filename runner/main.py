import os
import datetime
import serial
from client import set_initiator, set_reflector, set_none
from dataprocessing import DataPlotter
import time

def main():
    # Create the top-level measurements folder
    measurements_folder = "measurements"
    os.makedirs(measurements_folder, exist_ok=True)

    # Create timestamped folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_folder = os.path.join(measurements_folder, timestamp)
    os.makedirs(timestamped_folder, exist_ok=True)

    serial_port1 = '/dev/ttyACM0'
    serial_port2 = '/dev/ttyACM1'
    serial_port3 = '/dev/ttyACM2'

    measurement_folders = []
    data_file_paths = []

    for i in range(1, 4):
        measurement_folder = os.path.join(timestamped_folder, f"measurement_{i}")
        os.makedirs(measurement_folder, exist_ok=True)
        measurement_folders.append(measurement_folder)

        # Create a unique data file for each measurement
        data_file_path = os.path.join(measurement_folder, "data_recorded.json")
        data_file_paths.append(data_file_path)

    # Measurement 1: between module 1 and module 2
    set_none(serial_port3)
    set_reflector(serial_port1)    
    set_initiator(serial_port2, measurement_folders[0])
    
    # Measurement 2: between module 2 and module 3
    set_none(serial_port1)
    set_reflector(serial_port2)    
    set_initiator(serial_port3, measurement_folders[1])
    
    # Measurement 3: between module 3 and module 1
    set_none(serial_port2)
    set_reflector(serial_port3)    
    set_initiator(serial_port1, measurement_folders[2])

    # Now we will plot data for each measurement
    for i, measurement_folder in enumerate(measurement_folders):
        figures_folder = os.path.join(measurement_folder, "figures")
        os.makedirs(figures_folder, exist_ok=True)

        plotter = DataPlotter(data_file_paths[i], figures_folder)
        plotter.plot_data()

if __name__ == "__main__":
    main()
