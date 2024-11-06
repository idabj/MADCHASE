import os
import datetime
import subprocess
from client import set_initiator, set_reflector, set_none
from dataprocessing import DataPlotter


def disable_wifi():
    """Disables Wi-Fi on the Raspberry Pi"""
    try:
        # Disable Wi-Fi using rfkill
        subprocess.run(["sudo", "rfkill", "block", "wifi"], check=True)
        print("Wi-Fi has been disabled.")
    except subprocess.CalledProcessError:
        print("Failed to disable Wi-Fi.")

def disable_bluetooth():
    """Disables Bluetooth on the Raspberry Pi"""
    try:
        # Disable Bluetooth using rfkill
        subprocess.run(["sudo", "rfkill", "block", "bluetooth"], check=True)
        print("Bluetooth has been disabled.")
    except subprocess.CalledProcessError:
        print("Failed to disable Bluetooth.")

def enable_wifi():
    """Enables Wi-Fi on the Raspberry Pi"""
    try:
        # Enable Wi-Fi using rfkill
        subprocess.run(["sudo", "rfkill", "unblock", "wifi"], check=True)
        print("Wi-Fi has been enabled.")
    except subprocess.CalledProcessError:
        print("Failed to enable Wi-Fi.")

def enable_bluetooth():
    """Enables Bluetooth on the Raspberry Pi"""
    try:
        # Enable Bluetooth using rfkill
        subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], check=True)
        print("Bluetooth has been enabled.")
    except subprocess.CalledProcessError:
        print("Failed to enable Bluetooth.")

def main():
    # Get user inputs
    measurement_name = input("Enter the measurement name: ")
    N = int(input("Enter the number of measurements (N): "))

    # Create the top-level folder for the measurement
    base_folder = os.path.join("measurements", measurement_name)
    os.makedirs(base_folder, exist_ok=True)

    # Disable Wi-Fi and Bluetooth before starting measurements
    disable_wifi()
    disable_bluetooth()

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

        # Plot data for each measurement (optional)
        # for data_file_path, i in zip(data_file_paths, range(len(data_file_paths))):
        #     plotter = DataPlotter(data_file_path, timestamped_folder, i + 1)
        #     plotter.plot_data()

    # Re-enable Wi-Fi and Bluetooth after measurements (optional)
    #enable_wifi()
    #enable_bluetooth()

if __name__ == "__main__":
    main()
