import os
import datetime
from client import read_serial_data
from dataprocessing import DataPlotter

def main():
    # Create the top-level measurements folder
    measurements_folder = "measurements"
    os.makedirs(measurements_folder, exist_ok=True)

    # Create timestamped folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_folder = os.path.join(measurements_folder, timestamp)

    os.makedirs(timestamped_folder, exist_ok=True)

    # Define paths for data and figures
    data_file_path = os.path.join(timestamped_folder, "data_recorded.json")
    figures_folder = os.path.join(timestamped_folder, "figures")

    os.makedirs(figures_folder, exist_ok=True)

    # Serial port of the initiator
    serial_port = '/dev/ttyACM0'
    
    read_serial_data(serial_port, timestamped_folder)
    
    plotter = DataPlotter(data_file_path, figures_folder)
    plotter.plot_data()

if __name__ == "__main__":
    main()
