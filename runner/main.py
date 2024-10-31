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

    # Serial ports
    serial_port1 = '/dev/ttyACM0'
    serial_port2 = '/dev/ttyACM1'
    serial_port3 = '/dev/ttyACM2'

    # Define paths for data files
    data_file_paths = [
        os.path.join(timestamped_folder, "data_measurement_1.json"),
        os.path.join(timestamped_folder, "data_measurement_2.json"),
        os.path.join(timestamped_folder, "data_measurement_3.json"),
    ]

    # Measurement 1: between 1 and 2
    set_none(serial_port3)
    set_reflector(serial_port1)    
    set_initiator(serial_port2, timestamped_folder, measurement_number = 1)
    
    # Measurement 2: between 2 and 3
    set_none(serial_port1)
    set_reflector(serial_port2)    
    set_initiator(serial_port3, timestamped_folder, measurement_number = 2)
    
    # Measurement 3: between 3 and 1
    set_none(serial_port2)
    set_reflector(serial_port3)    
    set_initiator(serial_port1, timestamped_folder, measurement_number = 3)

    # Plot data for each measurement
    for data_file_path, i in zip(data_file_paths, range(len(data_file_paths))):
        plotter = DataPlotter(data_file_path, timestamped_folder, i+1)
        plotter.plot_data()

if __name__ == "__main__":
    main()
