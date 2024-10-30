import serial
import json
import os

def read_serial_data(serial_port, folder_path, baud_rate=115200, timeout=1):
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
    os.makedirs(folder_path, exist_ok=True)

    # Open a file to save the data
    with open(os.path.join(folder_path, "data_recorded.json"), "w") as file:
        try:
            
                
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

    with open(os.path.join(folder_path, "data_recorded.json"), "w") as final_file:
        json.dump(data_records, final_file)

