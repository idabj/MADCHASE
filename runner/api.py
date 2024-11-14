import os
import logging
import json
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.signal as signal

logging.basicConfig(level=logging.INFO)
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
                logging.info(f"Reading {self.folder_path}")
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
            logging.error(f"Error: File not found at {self.folder_path}.")
        except ValueError as e:
            logging.error(f"Error: Unable to read data from JSON file. {e}")
        
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
        #self.measurements = []

    def list_measurements(self):
        """List all subfolders in the measurement folder."""
        folder_path = os.path.join(self.base_dir, self.folder_name)
        measurements = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        return measurements

    def list_files(self):
        """List all the measurement files, sorted by the last number in the filename."""
        if not os.path.isdir(self.folder_path):
            logging.error(f"Measurement folder '{self.folder_name}' does not exist.")
            return []

        individual_measurements = [f for f in os.listdir(self.folder_path) if os.path.isdir(os.path.join(self.folder_path, f))]
        measurements_json_fullpath = []

        # Iterate through the individual measurement folders
        for meas in individual_measurements:
            meas_folder_path = os.path.join(self.folder_path, meas)

            # Get all JSON files from the measurement folder
            json_files = [f for f in os.listdir(meas_folder_path) if f.endswith('.json')]

            # Sort the JSON files by the number in the filename
            json_files_sorted = sorted(json_files, key=self._extract_measurement_number)

            # Append the full path of each sorted JSON file to the list
            for json_file in json_files_sorted:
                full_path = os.path.join(meas_folder_path, json_file)
                measurements_json_fullpath.append(full_path)

        logging.debug(f"Sorted files: {measurements_json_fullpath}")
        return measurements_json_fullpath

    def read_measurement(self, file_path):
        """Read a measurement from the given file path."""
        measurement = Measurement(file_path)
        measurement.read_data()
        return measurement
    
    def _extract_measurement_number(self, file_name):
        """Extracts the number from filenames of the format *_{num}.json."""
        match = re.search(r'_(\d+)\.json$', file_name)
        if match:
            return int(match.group(1))  # Return the numeric part as integer
        return float('inf')  #


class MeasurementProcessor:
    """Handles the overall process of reading and analyzing measurements."""
    
    def __init__(self, base_dir, folder_name):
        self.folder = MeasurementFolder(base_dir, folder_name)
    
    def get_IQ(self, index):
        """Get IQ data for a specific measurement by index."""
        files = self.folder.list_files()
        num_measurements = len(files) // 3

        if index >= num_measurements:
            logging.error(f"Index {index} out of range. Max index is {num_measurements - 1}.")
            os._exit(1)

        grouped_files = [files[i:i + 3] for i in range(0, len(files), 3)]
        selected_files = grouped_files[index]
        
        iq_data = [self.folder.read_measurement(file).get_IQ() for file in selected_files]
        
        if any(data is None for data in iq_data):
            logging.error(f"Failed to read IQ data for measurement {index}.")
            return None
        
        logging.debug(f"iq_data.shape {np.array(iq_data).shape}")
        return np.array(iq_data)

    def get_distance(self, index):
            """Get distance estimates for a specific measurement by index."""
            files = self.folder.list_files()
            num_measurements = len(files) // 3  # Assuming 3 files per measurement

            if index >= num_measurements:
                logging.error(f"Index {index} out of range. Max index is {num_measurements - 1}.")
                os._exit(1)

            # Group the files in sets of 3 (similar to how IQ data is grouped)
            grouped_files = [files[i:i + 3] for i in range(0, len(files), 3)]
            selected_files = grouped_files[index]
            
            # Retrieve the distance data from the selected files
            distance_data = [self.folder.read_measurement(file).get_distance() for file in selected_files]
            
            # Check for any missing or invalid distance data
            if any(data is None for data in distance_data):
                logging.error(f"Failed to read distance data for measurement {index}.")
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
                "highprec": highprec
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

        self.transfer = np.multiply(smag, np.exp(1j * sang))  # Corrected transfer function

    def calcImpulse(self):
        """Calculate the impulse response."""
        N = 2048  # Length of FFT
        transfer = self.transfer
        yfft = np.fft.ifft(self.transfer, N)  # Inverse FFT to get the impulse response
        
        
        yf = yfft[0:len(yfft)//2]  # Take the positive frequency part

        # Return the impulse response and the corresponding time axis
        self.impulse = yf
        self.impulse_x = np.arange(0, N / 2) / N / 1e6  # Time in microseconds
        return self.impulse, self.impulse_x

    def get_impulse(self, index, channel):
        """Get the impulse response for a specific measurement index."""
        iq_data = self.get_IQ(index)[channel]  # This is assuming get_IQ is implemented
        if iq_data is None:
            logging.error("Failed to get IQ data.")
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
    
    def get_multipath(self, index, channel):
        """Returns second peak in ns"""
        impulse = self.get_impulse(index, channel)
        logging.info(f"Impulse: {impulse[0]}")
        reflection = signal.find_peaks(abs(impulse[0]))
        logging.info(f"Reflection: {reflection}")
        return reflection

##########################################USAGE##################################################################################

def plot_constellation(BASE_DIR, measurement_name, colors=['tab:blue', 'tab:green', 'tab:red']):
    # Create a figure with 3 subplots, one for each channel
    fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
    fig.suptitle(f"Constellation Plots for Measurement '{measurement_name}'")
    
    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3
    
    channels = [0, 1, 2]  # CH1, CH2, CH3
    
    for i, channel in enumerate(channels):
        # Plot constellation for each measurement in the channel
        for k in range(int(num_meas)):
            iq_data = meas_processor.get_IQ(k)[channel]  # Get I/Q data for the given channel
            
            # Extract the I and Q components (i_local, q_local, i_remote, q_remote)
            i_local = iq_data[0]
            q_local = iq_data[1]
            
            i_remote = iq_data[2]
            q_remote = iq_data[3]
            
            # Plot the I/Q data on the constellation plot
            ax[1,i].scatter(i_local, q_local, color=colors[i], s=5, alpha=0.2)  # scatter plot for the local I/Q
            ax[0,i].scatter(i_remote, q_remote, color=colors[i], s=5, alpha=0.2)  # scatter plot for the local I/Q
            
        # Customize the plot for this channel
        ax[1,i].set_xlabel("In-Phase (I)")
        ax[1,i].set_ylabel("Quadrature (Q)")
        ax[1,i].set_title(f"Channel {channel + 1} Local")
        ax[1,i].grid(True)
        ax[1,i].set_aspect('equal')  # To make sure the axes have the same scale
        
        ax[0,i].set_xlabel("In-Phase (I)")
        ax[0,i].set_ylabel("Quadrature (Q)")
        ax[0,i].set_title(f"Channel {channel + 1} Remote")
        ax[0,i].grid(True)
        ax[0,i].set_aspect('equal')  # To make sure the axes have the same scale


    # Save the figure
    fig.savefig(save_folder_path+f"constellation_{measurement_name}.png", dpi=400)

def plot_time_domain(BASE_DIR, measurement_name, colors=['tab:blue', 'tab:green', 'tab:red']):
    # Create a figure with 3 subplots, one for each channel
    fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
    fig.suptitle(f"Constellation Plots for Measurement '{measurement_name}'")
    
    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3
    
    channels = [0, 1, 2]  # CH1, CH2, CH3
    
    for i, channel in enumerate(channels):
        # Plot constellation for each measurement in the channel
        for k in range(int(num_meas)):
            iq_data = meas_processor.get_IQ(k)[channel]  # Get I/Q data for the given channel
            
            # Extract the I and Q components (i_local, q_local, i_remote, q_remote)
            i_local = iq_data[0]
            q_local = iq_data[1]
            local = i_local + 1j*q_local
            
            i_remote = iq_data[2]
            q_remote = iq_data[3]
            remote = i_remote + 1j*q_remote
            logging.info(f"Shape remote signal: {remote.shape}")
            fs = 1e6
            time_vector = np.linspace(0, 1/fs*len(remote),len(remote))*10**6
            
            # Plot the I/Q data on the constellation plot
            ax[1,i].plot(time_vector, local, color=colors[i], alpha=0.5) 
            ax[0,i].plot(time_vector, remote, color=colors[i], alpha=0.5)  
            #ax[1,i].stem(time_vector, local, linefmt=colors[i], markerfmt=colors[i], basefmt=" ") 
            #ax[0,i].stem(time_vector, remote, linefmt=colors[i], markerfmt=colors[i], basefmt=" ")  
            
        # Customize the plot for this channel
        ax[1,i].set_xlabel("Time (ms)")
        ax[1,i].set_ylabel("Magnitude")
        ax[1,i].set_title(f"Channel {channel + 1} Local")
        ax[1,i].grid(True)
        ax[1,i].set_xlim([5,10])
    
        ax[0,i].set_xlabel("Time (ms)")
        ax[0,i].set_ylabel("Magnitude")
        ax[0,i].set_title(f"Channel {channel + 1} Remote")
        ax[0,i].grid(True)
        ax[0,i].set_xlim([5,10])


    # Save the figure
    fig.savefig(save_folder_path+f"time_domain_{measurement_name}.png", dpi=400)



def plot_impulse(BASE_DIR, measurement_name, linestyles=['-', '--'], colors=['tab:blue', 'tab:green', 'tab:red']):
    fig, ax = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True)
    fig.suptitle(f"Measurement '{measurement_name}'")
    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3
    
    channels = [0, 1, 2]  # CH1, CH2, CH3
    
    for i, channel in enumerate(channels):
        channel_avg = np.zeros_like(meas_processor.get_impulse(0, channel))
        all_impulses = []
        time_vector = None
        
        for k in range(int(num_meas)):
            impulse = meas_processor.get_impulse(k, channel)
            
            if time_vector is None:
                time_vector = impulse[0]*10**9  # Set the reference time vector from the first measurement
    
            all_impulses.append(abs((impulse[1]/np.max(impulse[1]))**2))  # Collect the impulse data

            # Plot individual measurements in gray
            #ax[i].plot(time_vector, abs((impulse[1]/np.max(impulse[1]))**2), linestyles[1], color="gray", alpha=0.3)

        # Convert all_impulses to a numpy array for easier manipulation
        all_impulses = np.array(all_impulses)
        logging.info(f"All impulses shape: {all_impulses.shape}")
        
        # Calculate standard deviation for each time point across all measurements
        channel_std = np.std(all_impulses, axis=0)
        channel_avg = np.average(all_impulses, axis=0)
        logging.info(f"Channel std: {channel_std.shape} channel avg: {channel_avg.shape}")
        
        # Peak calculation: Find the peak in the average impulse response
        peak_idx = np.argmax(channel_avg)  # Find the index of the peak
        peak_time = time_vector[peak_idx]  # Time of peak in ns
        peak_value = channel_avg[peak_idx]  # Value at the peak

        # Plot the average impulse
        ax[i].plot(time_vector, channel_avg, color=colors[i], label=f"Average")
        
        # Plot the peak point
        ax[i].plot(peak_time, peak_value, 'o', color=colors[i], label=f"Peak: {abs(peak_time):.2f}ns")
        
        # Plot the standard deviation as a shaded region around the average
        ax[i].fill_between(time_vector, 
                            (channel_avg - channel_std), 
                            (channel_avg + channel_std), 
                            color=colors[i], alpha=0.2, label=f"Standard Deviation")
        
        # Plot settings
        ax[i].set_xlim([0, 50])
        ax[i].set_xlabel("Time (ns)")
        ax[i].set_ylabel("Magnitude Squared |Impulse|^2")
        ax[i].set_title(f"Channel {channel+1}")
        ax[i].grid()
        ax[i].legend()
   
    # Save the figure
    fig.savefig(save_folder_path+f"avg_std_{measurement_name}.png", dpi=400)
    
def plot_position(BASE_DIR, measurement_data, devices_pos, linestyles=['-', '--'], device_colors=['tab:blue', 'goldenrod', 'tab:red'], ellipse_colors=['tab:green', 'tab:orange', 'tab:purple']):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6), constrained_layout=True)
    
    distance_measurements = ["fft", "phase_slope", "best", "highprec"]

    measurement_name, measurement_index = measurement_data[0]  # Only plot one measurement
    measprocessor = MeasurementProcessor(BASE_DIR, measurement_name)
    channel_indices = [0,1,2]
    
    distances = [measprocessor.get_multipath(measurement_index, index) for index in channel_indices]
    logging.info(f"Distances based on multipath: {distances}")
    
    for i, meas in enumerate(distance_measurements):
        distances = measprocessor.get_distance(measurement_index)[meas]
        ax = axs[i // 2, i % 2]  # 2x2 grid indexing

        ax.set_title(f"{measurement_name} - {meas} Distance Estimate")

        #channel_devices = [(0, 1), (1, 2), (2, 0)]
        channel_devices = [(1, 2), (2, 0),(0, 1)]
        #channel_devices = [(2, 0),(0, 1),(1, 2)]

        device_labels = [False, False, False]  # Track if a device is already labeled
        ellipse_idx = 0  # Index for ellipse colors

        for j, distance in enumerate(distances):
            semi_major = distance / 1000
            semi_minor = semi_major / 2

            focal_point1 = devices_pos[:, channel_devices[j][0]]
            focal_point2 = devices_pos[:, channel_devices[j][1]]

            center = (focal_point1 + focal_point2) / 2
            direction_vector = focal_point2 - focal_point1
            angle = np.arctan2(direction_vector[1], direction_vector[0]) * 180 / np.pi

            ellipse = patches.Ellipse(
                center,
                width=2 * semi_major,
                height=2 * semi_minor,
                angle=angle,
                edgecolor=ellipse_colors[ellipse_idx],  # Use separate color for ellipses
                facecolor='none',
                linewidth=2
            )

            ax.add_patch(ellipse)
            
            # Only add device labels if they haven't been labeled yet
            if not device_labels[channel_devices[j][0]]:
                ax.plot(devices_pos[0, channel_devices[j][0]], devices_pos[1, channel_devices[j][0]], "o", color=device_colors[channel_devices[j][0]], label=f"Device {channel_devices[j][0]+1}")
                device_labels[channel_devices[j][0]] = True
            if not device_labels[channel_devices[j][1]]:
                ax.plot(devices_pos[0, channel_devices[j][1]], devices_pos[1, channel_devices[j][1]], "o", color=device_colors[channel_devices[j][1]], label=f"Device {channel_devices[j][1]+1}")
                device_labels[channel_devices[j][1]] = True

            ax.plot(center[0], center[1], label=f"Channel {j + 1}", color=ellipse_colors[ellipse_idx])
            
            ellipse_idx += 1  # Move to the next ellipse color

        ax.set_aspect('equal', 'box')
        ax.set_xlabel("Position x [m]")
        ax.set_ylabel("Position y [m]")
        ax.grid()

        if i == 2:  # Only add the legend to the bottom-right subplot
            ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0., fontsize='small')

    plt.savefig(save_folder_path+"test_position.png", dpi=400, bbox_inches='tight')


CH1, CH2, CH3 = 0,1,2
I_LOCAL, Q_LOCAL, I_REMOTE, Q_REMOTE = 0, 1, 2, 3

# Example usage:
BASE_DIR = "measurements/"
measurement_data = [('empty', 8), ('reflector_rotate_2', 3)]

devices_pos = np.array([[1.88, 5.10, 7], [2.25, 0.74, 2.25]]) # row0 = x pos, row1 = y pos
save_folder_path = "/home/ida/Documents/obsidian/00 Prosjektoppgåve/Fordypningsprosjekt/figures/measurements/"
#plot_impulse_responses(BASE_DIR, measurement_data)
measurement_names = ["empty", "reflector", "reflector_rotate", "scatter"]
for measurement_name in measurement_names:
    plot_impulse(BASE_DIR, measurement_name)
    plot_constellation(BASE_DIR, measurement_name)
    plot_time_domain(BASE_DIR, measurement_name)
#plot_position(BASE_DIR, measurement_data, devices_pos)


