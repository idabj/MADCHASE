import os
import datetime
import time
from client import set_initiator, set_reflector, set_none

def take_measurement(serial_ports, timestamped_folder, measurement_number):
    """
    Function to execute the process for a specific measurement.
    Each measurement generates 3 data files in the timestamped folder.
    """
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

    for file_path in data_file_paths:
        if os.path.isdir(file_path):
            print(f"Error: {file_path} is a directory, not a file!")
            return []
        elif os.path.exists(file_path) and not os.path.isfile(file_path):
            print(f"Error: {file_path} exists but is not a file!")
            return []

    for data_file in data_file_paths:
        if os.path.exists(data_file):
            print(f"Warning: {data_file} already exists, overwriting...")

    # Measurement 1: between 1 and 2
    set_none(serial_ports[2])  # No initiator
    set_reflector(serial_ports[0])  # Reflector on serial_port1    
    print(f"Running measurement 1: {data_file_paths[0]}")
    set_initiator(serial_ports[1], data_file_paths[0], measurement_number=measurement_number)
    time.sleep(1.5)  
    
    # Measurement 2: between 2 and 3
    set_none(serial_ports[0])  # No initiator
    set_reflector(serial_ports[1])  # Reflector on serial_port2    
    print(f"Running measurement 2: {data_file_paths[1]}")
    set_initiator(serial_ports[2], data_file_paths[1], measurement_number=measurement_number)
    time.sleep(1.5)  
    
    # Measurement 3: between 3 and 1
    set_none(serial_ports[1])  # No initiator
    set_reflector(serial_ports[2])  # Reflector on serial_port3    
    print(f"Running measurement 3: {data_file_paths[2]}")
    set_initiator(serial_ports[0], data_file_paths[2], measurement_number=measurement_number)
    time.sleep(1.5)  

    for data_file in data_file_paths:
        if not os.path.exists(data_file):
            print(f"Error: {data_file} not found!")
        else:
            print(f"Data file found: {data_file}")

    return data_file_paths  


def main():
    measurement_name = input("Enter a name for this series of measurements: ")

    measurements_folder = "measurements"
    os.makedirs(measurements_folder, exist_ok=True)

    N = int(input("How many measurements would you like to take? "))

    serial_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']

    series_folder = os.path.join(measurements_folder, measurement_name)
    os.makedirs(series_folder, exist_ok=True)

    series_folder = os.path.abspath(series_folder)

    for i in range(N):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_folder = os.path.join(series_folder, f"measurement_{i+1}_{timestamp}")
        os.makedirs(timestamped_folder, exist_ok=True)

        timestamped_folder = os.path.abspath(timestamped_folder)

        data_file_paths = take_measurement(serial_ports, timestamped_folder, measurement_number=i+1)

        if not data_file_paths:
            continue

        time.sleep(1.5)


if __name__ == "__main__":
    main()
