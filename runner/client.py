import os
import json
import serial

def set_initiator(serial_port, folder_path, measurement_number, baud_rate=115200, timeout=1):
    """
    Reads data from a serial port and saves it as JSON files in the specified folder.

    Parameters:
        serial_port (str): The serial port to connect to.
        folder_path (str): The folder where the JSON files will be saved.
        baud_rate (int): The baud rate for the serial connection (default: 115200).
        timeout (int): The timeout for reading from the serial port (default: 1 second).
    """
    data_records = []  # List to store parsed JSON data

    # Ensure the folder exists
    #os.makedirs(folder_path, exist_ok=True)

    # Construct the file path
    file_path = folder_path
    
    # Check if the path is a directory (instead of a file) before opening
    if os.path.isdir(file_path):
        print(f"Error: {file_path} is a directory, not a file!")
        return  # Exit the function early to avoid further issues

    try:
        # Open the file for writing data
        with open(file_path, "w") as file:
            try:
                # Open serial connection
                with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
                    print(f"Connected to {serial_port} at {baud_rate} baud.")
                    ser.write(b'i')

                    try:
                        line = ser.readline().decode("utf-8").strip()
                        print(f"Received: {line}")

                        # Parse JSON data
                        data = json.loads(line)  # Expecting a JSON object

                        # Store data in the list
                        data_records.append(data)

                        # Write to file
                        json.dump(data, file)
                        file.write("\n")  # Write a newline for separation

                    except json.JSONDecodeError:
                        print(f"Invalid JSON format: {line}")
                    except Exception as e:
                        print(f"Error reading from serial port: {e}")

            except serial.SerialException as e:
                print(f"Error opening serial port: {e}")
            except KeyboardInterrupt:
                print("Exiting...")
            finally:
                print("Serial port closed.")
        
        # Write the complete list of data records at the end
        with open(file_path, "w") as final_file:
            json.dump(data_records, final_file)

    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")



def set_reflector(serial_port):
    with serial.Serial(serial_port, 115200, timeout=1) as ser:
        print(f"Connected to {serial_port}")
        ser.write(b'r')
        line = ser.readline().decode("utf-8").strip()
        print(f"Received: {line}")
        
def set_none(serial_port):
    with serial.Serial(serial_port, 115200, timeout=1) as ser:
        print(f"Connected to {serial_port}")
        ser.write(b'n')
        line = ser.readline().decode("utf-8").strip()
        print(f"Received: {line}")