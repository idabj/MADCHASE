import os
import datetime
from client import set_initiator, set_reflector, set_none
from dataprocessing import DataPlotter


def main():
    # Get user inputs
    measurement_name = input("Enter the measurement name: ")
    N = int(input("Enter the number of measurements (N): "))

    # Create the top-level folder for the measurement
    base_folder = os.path.join("measurements", measurement_name)
    os.makedirs(base_folder, exist_ok=True)

    # Loop N times to perform the measurements
    for i in range(N):
        # Create timestamped folder for this round of measurements
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_folder = os.path.join(base_folder, timestamp)
        os.makedirs(timestamped_folder, exist_ok=True)

        # Serial ports
        serial_port1 = '/dev/ttyACM0'
        serial_port2 = '/dev/ttyACM1'
        serial_port3 = '/dev/ttyACM2'

        # Define paths for data files for this measurement
        data_file_paths = [
            os.path.join(timestamped_folder, f"data_measurement_1_{timestamp}.json"),
            os.path.join(timestamped_folder, f"data_measurement_2_{timestamp}.json"),
            os.path.join(timestamped_folder, f"data_measurement_3_{timestamp}.json"),
        ]

        # Measurement 1: between 1 and 2
        set_none(serial_port3)
        set_reflector(serial_port1)
        set_initiator(serial_port2, timestamped_folder, measurement_number=1)

        # Measurement 2: between 2 and 3
        set_none(serial_port1)
        set_reflector(serial_port2)
        set_initiator(serial_port3, timestamped_folder, measurement_number=2)

        # Measurement 3: between 3 and 1
        set_none(serial_port2)
        set_reflector(serial_port3)
        set_initiator(serial_port1, timestamped_folder, measurement_number=3)

        # Plot data for each measurement
        #for data_file_path, i in zip(data_file_paths, range(len(data_file_paths))):
        #    plotter = DataPlotter(data_file_path, timestamped_folder, i + 1)
        #    plotter.plot_data()


if __name__ == "__main__":
    main()
