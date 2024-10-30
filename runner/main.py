import os
import datetime
import serial
from client import read_serial_data
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

    # Define paths for data and figures
    data_file_path = os.path.join(timestamped_folder, "data_recorded.json")
    figures_folder = os.path.join(timestamped_folder, "figures")

    os.makedirs(figures_folder, exist_ok=True)

    serial_port1 = '/dev/ttyACM0'
    serial_port2 = '/dev/ttyACM1'
    
    baud_rate=115200
    timeout=1
    
    with serial.Serial(serial_port1, baud_rate, timeout=timeout) as ser:
        print(f"Connected to {serial_port1} at {baud_rate} baud.")
        ser.write(b'r')
        line = ser.readline().decode("utf-8").strip()
        print(f"Received: {line}")
        
                    
    
    read_serial_data(serial_port2, timestamped_folder)

    plotter = DataPlotter(data_file_path, figures_folder)
    plotter.plot_data()

if __name__ == "__main__":
    main()
