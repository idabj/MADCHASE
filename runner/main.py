import os
import datetime
import time
from client import set_initiator, set_reflector, set_none
from dataprocessing import DataPlotter

def take_measurement(serial_ports, timestamped_folder, measurement_number):
    """
    Function to execute the process for a specific measurement.
    Each measurement generates 3 data files in the timestamped folder.
    """
    # Ensure the timestamped folder exists (should already exist, but double check)
    if not os.path.exists(timestamped_folder):
        print(f"Error: Timestamped folder {timestamped_folder} does not exist!")
        return []

    # Create the absolute data file paths for each measurement in the timestamped folder
    data_file_paths = [
        os.path.join(timestamped_folder, f"data_measurement_{measurement_number}_1.json"),
        os.path.join(timestamped_folder, f"data_measurement_{measurement_number}_2.json"),
        os.path.join(timestamped_folder, f"data_measurement_{measurement_number}_3.json"),
    ]

    print(f"Data files for measurement {measurement_number}: {data_file_paths}")

    # Ensure the file paths point to files, not directories
    for file_path in data_file_paths:
        if os.path.isdir(file_path):
            print(f"Error: {file_path} is a directory, not a file!")
            return []
        elif os.path.exists(file_path) and not os.path.isfile(file_path):
            print(f"Error: {file_path} exists but is not a file!")
            return []

    # Check if files already exist, this could help with debugging
    for data_file in data_file_paths:
        if os.path.exists(data_file):
            print(f"Warning: {data_file} already exists, overwriting...")

    # Measurement 1: between 1 and 2
    set_none(serial_ports[2])  # No initiator
    set_reflector(serial_ports[0])  # Reflector on serial_port1    
    print(f"Running measurement 1: {data_file_paths[0]}")
    set_initiator(serial_ports[1], data_file_paths[0], measurement_number=measurement_number)
    time.sleep(1.5)  # Increased sleep time to ensure file is fully written
    
    # Measurement 2: between 2 and 3
    set_none(serial_ports[0])  # No initiator
    set_reflector(serial_ports[1])  # Reflector on serial_port2    
    print(f"Running measurement 2: {data_file_paths[1]}")
    set_initiator(serial_ports[2], data_file_paths[1], measurement_number=measurement_number)
    time.sleep(1.5)  # Increased sleep time to ensure file is fully written
    
    # Measurement 3: between 3 and 1
    set_none(serial_ports[1])  # No initiator
    set_reflector(serial_ports[2])  # Reflector on serial_port3    
    print(f"Running measurement 3: {data_file_paths[2]}")
    set_initiator(serial_ports[0], data_file_paths[2], measurement_number=measurement_number)
    time.sleep(1.5)  # Increased sleep time to ensure file is fully written

    # Check if files exist after measurements
    for data_file in data_file_paths:
        if not os.path.exists(data_file):
            print(f"Error: {data_file} not found!")
        else:
            print(f"Data file found: {data_file}")

    return data_file_paths  # Return the paths to the generated data files


def main():
    # Ask user for a name for the measurement series
    measurement_name = input("Enter a name for this series of measurements: ")

    # Create the top-level measurements folder if it doesn't exist
    measurements_folder = "measurements"
    os.makedirs(measurements_folder, exist_ok=True)

    # Ask user how many measurements to take
    N = int(input("How many measurements would you like to take? "))

    # Serial ports (assuming we have 3 serial ports for the measurements)
    serial_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']

    # Create a parent folder for the measurements based on the series name
    series_folder = os.path.join(measurements_folder, measurement_name)
    os.makedirs(series_folder, exist_ok=True)

    # Get the absolute path for the series folder
    series_folder = os.path.abspath(series_folder)

    # Loop through N measurements, creating timestamped subfolders for each one
    for i in range(N):
        # Create a timestamped folder for each measurement
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_folder = os.path.join(series_folder, f"measurement_{i+1}_{timestamp}")
        os.makedirs(timestamped_folder, exist_ok=True)

        # Get the absolute path of the timestamped folder
        timestamped_folder = os.path.abspath(timestamped_folder)

        # Take measurements and get the data file paths
        data_file_paths = take_measurement(serial_ports, timestamped_folder, measurement_number=i+1)

        # If no data files were generated, skip plotting
        if not data_file_paths:
            continue

        # Plot data for this measurement
        for data_file_path, j in zip(data_file_paths, range(len(data_file_paths))):
            # Initialize the DataPlotter with correct absolute file paths
            print(f"Plotting data for {data_file_path}")
            plotter = DataPlotter(data_file_path, timestamped_folder, j+1)
            plotter.plot_data()

        # Wait a short time before starting the next measurement
        time.sleep(1.5)


if __name__ == "__main__":
    main()
