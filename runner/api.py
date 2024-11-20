import os
import logging
import json
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.signal as signal
from algorithms import *



class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())


logger.addHandler(ch)

class Measurement:
    """Represents a single measurement in a measurement folder."""

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.i_local = None
        self.q_local = None
        self.i_remote = None
        self.q_remote = None
        self.hopping_sequence = None
        self.sinr_local = None
        self.sinr_remote = None
        self.fft = None
        self.phase_slope = None
        self.rssi_openspace = None
        self.best = None
        self.highprec = None
        self.link_loss = None
        self.duration = None
        self.rssi_local = None
        self.rssi_remote = None
        self.txpwr_local = None
        self.txpwr_remote = None
        self.quality = None

    def read_data(self):
        """Read data from the JSON file."""
        try:
            with open(self.folder_path, "r") as file:
                #logger.info(f"Reading {self.folder_path}")
                data = json.load(file)
                record = data[0]  # Assume we need the first record

                # Assign the values from the JSON to instance variables
                self.i_local = np.array(record["i_local"])
                self.q_local = np.array(record["q_local"])
                self.i_remote = np.array(record["i_remote"])
                self.q_remote = np.array(record["q_remote"])
                self.hopping_sequence = np.array(record["hopping_sequence"])
                self.sinr_local = np.array(record["sinr_local"])
                self.sinr_remote = np.array(record["sinr_remote"])
                self.fft = record["ifft[mm]"]
                self.phase_slope = record["phase_slope[mm]"]
                self.rssi_openspace = record["rssi_openspace[mm]"]
                self.best = record["best[mm]"]
                self.highprec = record["highprec[mm]"]
                self.link_loss = record["link_loss[dB]"]
                self.duration = record["duration[us]"]
                self.rssi_local = record["rssi_local[dB]"]
                self.rssi_remote = record["rssi_remote[dB]"]
                self.txpwr_local = record["txpwr_local[dB]"]
                self.txpwr_remote = record["txpwr_remote[dB]"]
                self.quality = record["quality"]

        except FileNotFoundError:
            logger.error(f"Error: File not found at {self.folder_path}.")
        except ValueError as e:
            logger.error(f"Error: Unable to read data from JSON file. {e}")

    def get_IQ(self):
        """Return I/Q data for this measurement"""
        return np.array([self.i_local, self.q_local, self.i_remote, self.q_remote])

    def get_distance(self):
        "Return distance measurements for this measurement"
        return self.fft, self.phase_slope, self.rssi_openspace, self.best, self.highprec


class MeasurementFolder:
    """Represents a folder containing multiple measurements."""

    def __init__(self, base_dir, folder_name):
        self.base_dir = base_dir
        self.folder_name = folder_name
        self.folder_path = os.path.join(base_dir, folder_name)
        # self.measurements = []

    def list_measurements(self):
        """List all subfolders in the measurement folder."""
        folder_path = os.path.join(self.base_dir, self.folder_name)
        measurements = [
            f
            for f in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, f))
        ]
        return measurements

    def list_files(self):
        """List all the measurement files, sorted by the last number in the filename."""
        if not os.path.isdir(self.folder_path):
            logger.error(f"Measurement folder '{self.folder_name}' does not exist.")
            return []

        individual_measurements = [
            f
            for f in os.listdir(self.folder_path)
            if os.path.isdir(os.path.join(self.folder_path, f))
        ]
        measurements_json_fullpath = []

        # Iterate through the individual measurement folders
        for meas in individual_measurements:
            meas_folder_path = os.path.join(self.folder_path, meas)

            # Get all JSON files from the measurement folder
            json_files = [
                f for f in os.listdir(meas_folder_path) if f.endswith(".json")
            ]

            # Sort the JSON files by the number in the filename
            json_files_sorted = sorted(json_files, key=self._extract_measurement_number)

            # Append the full path of each sorted JSON file to the list
            for json_file in json_files_sorted:
                full_path = os.path.join(meas_folder_path, json_file)
                measurements_json_fullpath.append(full_path)

        logger.debug(f"Sorted files: {measurements_json_fullpath}")
        return measurements_json_fullpath

    def read_measurement(self, file_path):
        """Read a measurement from the given file path."""
        measurement = Measurement(file_path)
        measurement.read_data()
        return measurement

    def _extract_measurement_number(self, file_name):
        """Extracts the number from filenames of the format *_{num}.json."""
        match = re.search(r"_(\d+)\.json$", file_name)
        if match:
            return int(match.group(1))  # Return the numeric part as integer
        return float("inf")  #


class MeasurementProcessor:
    """Handles the overall process of reading and analyzing measurements."""

    def __init__(self, base_dir, folder_name):
        self.folder = MeasurementFolder(base_dir, folder_name)

    def get_IQ(self, index):
        """Get IQ data for a specific measurement by index."""
        files = self.folder.list_files()
        num_measurements = len(files) // 3

        if index >= num_measurements:
            logger.error(
                f"Index {index} out of range. Max index is {num_measurements - 1}."
            )
            os._exit(1)

        grouped_files = [files[i : i + 3] for i in range(0, len(files), 3)]
        selected_files = grouped_files[index]

        iq_data = [
            self.folder.read_measurement(file).get_IQ() for file in selected_files
        ]

        if any(data is None for data in iq_data):
            logger.error(f"Failed to read IQ data for measurement {index}.")
            return None

        logger.debug(f"iq_data.shape {np.array(iq_data).shape}")
        return np.array(iq_data)

    def get_distance(self, index):
        """Get distance estimates for a specific measurement by index."""
        files = self.folder.list_files()
        num_measurements = len(files) // 3  # Assuming 3 files per measurement

        if index >= num_measurements:
            logger.error(
                f"Index {index} out of range. Max index is {num_measurements - 1}."
            )
            os._exit(1)

        # Group the files in sets of 3 (similar to how IQ data is grouped)
        grouped_files = [files[i : i + 3] for i in range(0, len(files), 3)]
        selected_files = grouped_files[index]

        # Retrieve the distance data from the selected files
        distance_data = [
            self.folder.read_measurement(file).get_distance() for file in selected_files
        ]

        # Check for any missing or invalid distance data
        if any(data is None for data in distance_data):
            logger.error(f"Failed to read distance data for measurement {index}.")
            return None

        # Unzip the distance data (fft, phase_slope, etc.) for each file
        fft, phase_slope, rssi_openspace, best, highprec = zip(*distance_data)

        # Convert to numpy arrays if needed for further processing
        fft = np.array(fft)
        phase_slope = np.array(phase_slope)
        rssi_openspace = np.array(rssi_openspace)
        best = np.array(best)
        highprec = np.array(highprec)

        # Return all distance estimates as a dictionary or a tuple
        return {
            "fft": fft,
            "phase_slope": phase_slope,
            "rssi_openspace": rssi_openspace,
            "best": best,
            "highprec": highprec,
        }

    def calcTransfer2(self):
        """Calculate the squared transfer function."""
        l = self.i_local + np.multiply(1j, self.q_local)  # Local data (complex)
        r = self.i_remote + np.multiply(1j, self.q_remote)  # Remote data (complex)

        self.remote = r
        self.local = l
        self.transfer2 = np.multiply(l, r)  # Transfer function: l * r

    def calcTransfer(self):
        """Calculate the transfer function with phase correction."""
        fstart = 4
        fstop = 78

        tr = np.zeros(len(self.transfer2), dtype=complex)

        # Linear regression to find optimum phase slope
        x = np.arange(fstart, fstop, 1)
        ang = np.unwrap(np.angle(self.transfer2))
        A = np.vstack([x, np.ones(len(x))]).T
        xang = np.linalg.lstsq(A, ang[fstart:fstop], rcond=None)[0]
        xall = np.arange(0, 80, 1)
        th_ideal = xang[0] / 2 * xall + xang[1] / 2
        smag = np.sqrt(np.abs(self.transfer2))
        sang = ang / 2

        # Phase correction to minimize the phase drift
        for i in range(fstart, fstop):
            at = th_ideal[i]
            diff = sang[i] - th_ideal[i]
            if diff > np.pi:
                sang[i] = sang[i] - np.pi
            elif diff < -np.pi:
                sang[i] = sang[i] + np.pi

        self.transfer = np.multiply(
            smag, np.exp(1j * sang)
        )  # Corrected transfer function
        self.sang = sang

    def calcImpulse(self):
        """Calculate the impulse response."""
        N = 2048  # Length of FFT
        transfer = self.transfer
        yfft = np.fft.ifft(self.transfer, N)  # Inverse FFT to get the impulse response

        yf = yfft[0 : len(yfft) // 2]  # Take the positive frequency part

        # Return the impulse response and the corresponding time axis
        self.impulse = yf
        self.impulse_x = np.arange(0, N / 2) / N / 1e6  # Time in microseconds
        return self.impulse, self.impulse_x

    def get_transfer(self, index, channel):
        """Get the transfer function for a specific measurement index."""
        iq_data = self.get_IQ(index)[channel]
        if iq_data is None:
            logger.error("Failed to get IQ data.")
            return None

        # Extract I/Q data for local and remote channels
        self.i_local, self.q_local, self.i_remote, self.q_remote = iq_data

        # Step 1: Calculate the transfer function
        self.calcTransfer2()
        self.calcTransfer()
        # Define frequency array
        N = len(self.transfer)
        sample_rate = 1e6  # Adjust this based on your actual sample rate
        frequency_vector = np.fft.fftshift(np.fft.fftfreq(N, d=1 / sample_rate))
        frequency_vector += abs(np.min(frequency_vector))

        logger.info(
            f"Frequency vector: {frequency_vector.shape} Transfer: {self.transfer.shape}"
        )

        return frequency_vector, self.transfer, self.sang

    def get_impulse(self, index, channel):
        """Get the impulse response for a specific measurement index."""
        iq_data = self.get_IQ(index)[channel]
        if iq_data is None:
            logger.error("Failed to get IQ data.")
            return None

        # Extract I/Q data for local and remote channels
        self.i_local, self.q_local, self.i_remote, self.q_remote = iq_data

        # Step 1: Calculate the transfer function
        self.calcTransfer2()
        self.calcTransfer()

        # Step 2: Calculate the impulse response
        impulse, impulse_x = self.calcImpulse()

        # Step 3: Return impulse response and time axis
        return impulse_x, impulse

    def get_music(self, index, channel, num_sources):
        """Returns second peak in ns"""
        iq = self.get_IQ(index)[channel]
        IQ = (iq[0] + 1j * iq[1]) * (iq[2] + 1j * iq[3])
        IQ = IQ[4:-4]  # Remove artifacts at start and end
        time_vector = np.linspace(0,40e-9,1000)
        music = t_music_time(
            IQ, 
            num_sources=num_sources, 
            candidate_delays=time_vector, 
            sampling_frequency=4e6, 
            num_taps=8, 
            tap_spacing=2
        )
        return time_vector, music
    
    def get_music_peaks(self, index, channel, num_sources=2):
        time_vector, music = self.get_music(index, channel, num_sources=num_sources)
        music = 20*np.log10(abs(music)**2)
        music -= np.max(music)
        
        peaks, _ = signal.find_peaks(music, height=-80)
        c = 3e8
        
        return time_vector[peaks]*c
    
    def get_distance_reflector(self, index, channel):
        time_vector_peaks = self.get_music_peaks(index, channel)
        
        if len(time_vector_peaks) > 1:
            distance_reflector = time_vector_peaks[1]
            return distance_reflector
        
        else:
            logger.warning("Less than two peaks in MUSIC pseudospectrogram")
            return 0



