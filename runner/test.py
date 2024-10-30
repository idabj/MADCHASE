import os
import datetime
import serial
from client import read_serial_data
from dataprocessing import DataPlotter
import time

serial_port1 = '/dev/ttyACM0'
serial_port2 = '/dev/ttyACM1'

with serial.Serial(serial_port1, 115200, timeout=5) as ser:
    print(f"Connected to {serial_port1}")
    ser.write(b'')
    line = ser.readline().decode("utf-8").strip()
print(f"Received: {line}")
