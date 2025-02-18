from api import *
from itertools import combinations
import matplotlib.pyplot as plt
import logging
from ellipse import *
import csv
import scipy

CH1, CH2, CH3 = 0, 1, 2


class MeasurementPlotter:
    def __init__(
        self, BASE_DIR, save_path, measurement_name, colors_ch, colors_devices
    ):
        self.save_path = save_path
        self.meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
        self.measurement_name = measurement_name
        self.num_meas = int(len(self.meas_processor.folder.list_files()) / 3)
        self.channels = [CH1, CH2, CH3]  # CH1, CH2, CH3
        self.num_channels = len(self.channels)
        self.devices = [
            (0, 2), 
            (2, 1),
            (0, 1),
        ]
        x_shift, y_shift = 0.5, 0.75
        self.devices_pos = np.array(
            [
                [1.88 + x_shift, 5.10 + x_shift, 7 + x_shift],
                [2.25 + y_shift, 0.74 + y_shift, 2.25 + y_shift],
            ]
        )

        self.object_pos = np.array([1.7 + x_shift, 0.74 + y_shift])

        self.linestyles = ["-", "--"]
        self.colors_ch = colors_ch
        self.colors_devices = colors_devices
        self.fs = 4e6

    def plot_constellation(self):
        fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
        fig.suptitle(f"Constellation Plots for Measurement '{self.measurement_name}'")

        fig_hist, ax_hist = plt.subplots(2, 3, figsize=(10,6), layout="constrained")
        fig_hist.suptitle(f'Histogram of constellation data - {self.measurement_name}')
        
        for i, channel in enumerate(self.channels):
            all_iq = []
            for k in range(int(self.num_meas)):
                iq_data = self.meas_processor.get_IQ(k)[channel]
                all_iq.append(iq_data)
                for j, (i_data, q_data, title_suffix) in enumerate(
                    [
                        (
                            iq_data[0],
                            iq_data[1],
                            f"Local\nDevice {self.devices[channel][0]+1}",
                        ),
                        (
                            iq_data[2],
                            iq_data[3],
                            f"Remote\nDevice {self.devices[channel][1]+1}",
                        ),
                    ]
                ):
                    ax[j, i].scatter(
                        i_data, q_data, color=self.colors_ch[i], s=5, alpha=0.2
                    )
                    ax[j, i].set_title(f"Channel {channel + 1} {title_suffix}")
                    ax[j, i].set_xlabel("In-Phase (I)")
                    ax[j, i].set_ylabel("Quadrature (Q)")
                    ax[j, i].set_aspect("equal")
                    ax[j, i].set_xlim([-9000, 9000])
                    ax[j, i].set_ylim([-9000, 9000])
                    ax[j, i].grid(
                        which="major",
                        linestyle="-",
                        linewidth="0.8",
                        color="darkgray",
                        alpha=0.8,
                    )
                    ax[j, i].grid(
                        which="minor",
                        linestyle=":",
                        linewidth="0.5",
                        color="gray",
                        alpha=0.7,
                    )
                    ax[j, i].minorticks_on()
                    
            all_iq = np.concatenate(np.array(all_iq), axis=1)
            logger.info(f"Shape of all_iq: {all_iq.shape}")
            mag_local = np.sqrt(all_iq[0,:]**2 + all_iq[1,:]**2)
            ax_hist[0, i].hist(mag_local, bins=15, color=self.colors_ch[i], alpha=0.7, edgecolor='black')
            ax_hist[0, i].set_title(f"Channel {i+1} - Local")
            ax_hist[0, i].set_xlabel('Received value')
            ax_hist[0, i].set_ylabel('Frequency')
            ax_hist[0, i].grid(axis='y', linestyle='--', alpha=0.7)
            ax_hist[0, i].set_xlim([0, 8000])
            ax_hist[0, i].set_ylim([0, 1000])
            
            mag_remote = np.sqrt(all_iq[2,:]**2 + all_iq[3,:]**2)
            ax_hist[1, i].hist(mag_remote, bins=15, color=self.colors_ch[i], alpha=0.7, edgecolor='black')
            ax_hist[1, i].set_title(f"Channel {i+1} - Remote")
            ax_hist[1, i].set_xlabel('Received value')
            ax_hist[1, i].set_ylabel('Instances')
            ax_hist[1, i].grid(axis='y', linestyle='--', alpha=0.7)
            ax_hist[1, i].set_xlim([0, 8000])
            ax_hist[1, i].set_ylim([0, 1000])
            
            # Filter out zeros
            nonzero_mag_local = mag_local[mag_local > 0]
            nonzero_mag_remote = mag_remote[mag_remote > 0]

            # Calculate mean of nonzero values
            mean_local = np.mean(nonzero_mag_local)
            mean_remote = np.mean(nonzero_mag_remote)
            
            sd_local = np.std(nonzero_mag_local)
            sd_remote = np.std(nonzero_mag_remote) 


            # Add vertical lines for the means
            ax_hist[0, i].axvline(mean_local, color='red', linestyle='--', label=f'Mean: {mean_local:.0f}')
            ax_hist[1, i].axvline(mean_remote, color='red', linestyle='--', label=f'Mean: {mean_remote:.0f}')
            
            ax_hist[0, i].plot([],'o', color='blue', linestyle='--', label=f'SD: {sd_local:.0f}')
            ax_hist[1, i].plot([], 'o', color='blue', linestyle='--', label=f'SD: {sd_remote:.0f}')


            ax_hist[0, i].legend()
            ax_hist[1, i].legend()
            
        save_fig_path = self.save_path + f"constellation_{self.measurement_name}"
        fig.savefig(save_fig_path + ".svg")
        fig.savefig(save_fig_path + ".png", dpi=400)
        
        
        histogram_path = f"{self.save_path}/constellation_histogram_{self.measurement_name}"
        fig_hist.savefig(histogram_path + ".png")
        fig_hist.savefig(histogram_path + ".svg")

    def plot_time(self):
        fig, ax = plt.subplots(1, 3, figsize=(8, 3), constrained_layout=True)
        fig.suptitle(f"Combined IQ signal for measurement '{self.measurement_name}'")


        for i, channel in enumerate(self.channels):
            all_IQ = [
                (
                    self.meas_processor.get_IQ(idx_meas)[channel][0]
                    + 1j * self.meas_processor.get_IQ(idx_meas)[channel][1]
                )[4:-4]
                * (
                    self.meas_processor.get_IQ(idx_meas)[channel][2]
                    + 1j * self.meas_processor.get_IQ(idx_meas)[channel][3]
                )[4:-4]
                for idx_meas in range(int(self.num_meas))
            ]

            time_vector = (
                np.linspace(0, 1 / self.fs * len(all_IQ[0]), len(all_IQ[0])) * 10**6
            )
            IQ_avg = np.average(all_IQ, axis=0)
            IQ_std = np.std(all_IQ, axis=0)

            ax[i].plot(time_vector, IQ_avg, color=self.colors_ch[i], label="Average")
            ax[i].fill_between(
                time_vector,
                IQ_avg - IQ_std,
                IQ_avg + IQ_std,
                color=self.colors_ch[i],
                alpha=0.2,
                label="Standard Deviation",
            )
            ax[i].set_xlabel("Time (ms)")
            ax[i].set_ylabel("Magnitude")
            ax[i].set_title(f"Channel {channel + 1}")
            ax[i].grid(
                which="major",
                linestyle="-",
                linewidth="0.8",
                color="darkgray",
                alpha=0.8,
            )
            ax[i].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )
            ax[i].minorticks_on()
            
            


        save_fig_path = self.save_path + f"time_domain_{self.measurement_name}"
        fig.savefig(save_fig_path + ".svg")
        fig.savefig(
            save_fig_path + ".png",
            dpi=400,
        )

    def plot_transfer(self):
        fig, ax = plt.subplots(2, 3, figsize=(12, 5), constrained_layout=True)
        fig.suptitle(f"Measurement '{self.measurement_name}'")
        fig.patch.set_facecolor("white")
        fig.patch.set_alpha(0.0)
        for i, channel in enumerate(self.channels):
            channel_avg_mag = np.zeros_like(
                self.meas_processor.get_transfer(0, channel)[1]
            )
            channel_avg_phase = np.zeros_like(
                self.meas_processor.get_transfer(0, channel)[2]
            )
            all_transfers_mag = []
            all_transfers_phase = []
            frequency_vector = None

            for k in range(int(self.num_meas)):
                frequency, transfer_mag, transfer_phase = (
                    self.meas_processor.get_transfer(k, channel)
                )
                if frequency_vector is None:
                    frequency_vector = (frequency*10**6 + 2.4*10**9)*10**(-9)

                transfer_mag_db = 20 * np.log10(
                    abs(transfer_mag / np.max(transfer_mag))
                )
                transfer_mag_db = transfer_mag_db - np.max(transfer_mag_db)
                all_transfers_mag.append(transfer_mag_db)
                all_transfers_phase.append(transfer_phase)

                # Plot individual measurements in gray
                """
                ax[0, i].plot(
                    frequency_vector,
                    transfer_mag_db,
                    self.linestyles[1],
                    color="gray",
                    alpha=0.2,
                )
                ax[1, i].plot(
                    frequency_vector,
                    transfer_phase,
                    self.linestyles[1],
                    color="gray",
                    alpha=0.2,
                )
                """

            # Convert to numpy arrays
            all_transfers_mag = np.array(all_transfers_mag)
            all_transfers_phase = np.array(all_transfers_phase)

            # Calculate standard deviation and average
            channel_std_mag = np.std(all_transfers_mag, axis=0)
            channel_avg_mag = np.average(all_transfers_mag, axis=0)
            channel_std_phase = np.std(all_transfers_phase, axis=0)
            channel_avg_phase = np.average(all_transfers_phase, axis=0)

            # Find peaks and valleys
            peaks, _ = scipy.signal.find_peaks(channel_avg_mag)
            valleys, _ = scipy.signal.find_peaks(-channel_avg_mag)  # Invert the signal to find valleys

            # Plot magnitude
            ax[0, i].plot(
                frequency_vector,
                channel_avg_mag,
                color=self.colors_ch[i],
                label="Average",
            )

            # Mark peaks
            """
            ax[0, i].scatter(
                frequency_vector[peaks],
                channel_avg_mag[peaks],
                color="red",
                label="Peaks",
                zorder=5
            )

            # Mark valleys
            ax[0, i].scatter(
                frequency_vector[valleys],
                channel_avg_mag[valleys],
                color="blue",
                label="Valleys",
                zorder=5
            )

            """
            # Add labels and legend
            ax[0, i].set_title("Magnitude Response")
            ax[0, i].set_xlabel("Frequency")
            ax[0, i].set_ylabel("Magnitude")
            ax[0, i].legend()
            
            ax[0, i].fill_between(
                frequency_vector,
                (channel_avg_mag - channel_std_mag),
                (channel_avg_mag + channel_std_mag),
                color=self.colors_ch[i],
                alpha=0.2,
                label="Standard Deviation",
            )

            # Plot phase
            ax[1, i].plot(
                frequency_vector,
                channel_avg_phase,
                color=self.colors_ch[i],
                label="Average",
            )
            ax[1, i].fill_between(
                frequency_vector,
                (channel_avg_phase - channel_std_phase),
                (channel_avg_phase + channel_std_phase),
                color=self.colors_ch[i],
                alpha=0.2,
                label="Standard Deviation",
            )

            # Magnitude plot settings
            if i == 0:  # Add y-axis labels only for the first column
                ax[0, i].set_ylabel(r"Magnitude $|H(f)|$ [dB]")
                ax[1, i].set_ylabel("Phase [radians]")
            else:
                ax[0, i].set_yticklabels([])
                ax[1, i].set_yticklabels([])

            # Add x-axis labels only for the bottom row
            ax[0, i].patch.set_facecolor("white")
            ax[0, i].patch.set_alpha(1.0)
            ax[1, i].patch.set_facecolor("white")
            ax[1, i].patch.set_alpha(1.0)

            ax[0, i].set_xlabel("Frequency (GHz)")
            ax[1, i].set_xlabel("Frequency (GHz)")

            ax[0, i].set_ylim([-5, 0.5])
            ax[0, i].set_title(f"Channel {channel+1} Magnitude")
            ax[0, i].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            ax[0, i].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )
            ax[0, i].minorticks_on()
            ax[0, i].legend(loc="lower left")

            ax[1, i].set_ylim([-10, 2])
            ax[1, i].set_title(f"Channel {channel+1} Phase")
            ax[1, i].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            ax[1, i].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )
            ax[1, i].minorticks_on()
            ax[1, i].legend(loc="lower left")

        # Remove unused subplots (if any)
        for unused_ax in range(len(self.channels), ax.shape[1]):
            fig.delaxes(ax[0, unused_ax])
            fig.delaxes(ax[1, unused_ax])

        # Save the figure
        fig.savefig(
            self.save_path + f"transfer_{self.measurement_name}.svg",
            bbox_inches="tight",
            pad_inches=0.0,
        )
        fig.savefig(
            self.save_path + f"transfer_{self.measurement_name}.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.0,
        )

    def plot_impulse_ifft(self):
        fig, ax = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True)
        fig.suptitle(f"Measurement '{self.measurement_name}'")

        for i, channel in enumerate(self.channels):
            all_impulses = []
            time_vector = None

            for k in range(int(self.num_meas)):
                impulse = self.meas_processor.get_impulse(k, channel)
                # transfer = meas_processor.get_transfer(k, channel)[1]
                # impulse = music(2)
                if time_vector is None:
                    time_vector = (
                        impulse[0] * 10**9
                    )  # Set the reference time vector from the first measurement

                impulse_current = 20 * np.log10(
                    abs(impulse[1] / np.max(impulse[1])) ** 2
                )
                impulse_current = impulse_current - np.max(impulse_current)
                all_impulses.append(impulse_current)  # Collect the impulse data

                # Plot individual measurements in gray
                ax[i].plot(
                    time_vector,
                    impulse_current,
                    self.linestyles[1],
                    color="gray",
                    alpha=0.2,
                )

            # Convert all_impulses to a numpy array for easier manipulation
            all_impulses = np.array(all_impulses)
            # logger.info(f"All impulses shape: {all_impulses.shape}")

            # Calculate standard deviation for each time point across all measurements
            channel_std = np.std(all_impulses, axis=0)
            channel_avg = np.average(all_impulses, axis=0)
            # logger.info(
            # f"Channel std: {channel_std.shape} channel avg: {channel_avg.shape}"
            # )

            # Peak calculation: Find the peak in the average impulse response
            peak_idx = np.argmax(channel_avg)  # Find the index of the peak
            peak_time = time_vector[peak_idx]  # Time of peak in ns
            peak_value = channel_avg[peak_idx]  # Value at the peak

            # Plot the average impulse
            ax[i].plot(
                time_vector, channel_avg, color=self.colors_ch[i], label=f"Average"
            )

            # Plot the peak point
            ax[i].plot(
                peak_time,
                peak_value,
                "o",
                color=self.colors_ch[i],
                label=f"Peak: {abs(peak_time):.2f}ns",
            )

            # Plot the standard deviation as a shaded region around the average
            ax[i].fill_between(
                time_vector,
                (channel_avg - channel_std),
                (channel_avg + channel_std),
                color=self.colors_ch[i],
                alpha=0.2,
                label=f"Standard Deviation",
            )

            # Plot settings
            ax[i].set_xlim([0, 150])
            ax[i].set_ylim([-60, 0.5])
            ax[i].set_xlabel("Time (ns)")
            ax[i].set_ylabel("Magnitude Squared |Impulse|^2 [dB]")
            ax[i].set_title(f"Channel {channel+1}")
            ax[i].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            ax[i].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )

            ax[i].minorticks_on()
            ax[i].legend()

        # Save the figure
        fig.savefig(self.save_path + f"impulse_{self.measurement_name}.svg")
        fig.savefig(
            self.save_path + f"impulse_{self.measurement_name}.png",
            dpi=400,
        )

    def plot_impulse_music(self, num_sources, plot_individual=False):
        # Ensure num_sources is a list
        if isinstance(num_sources, int):
            num_sources = [num_sources]

        # Create subplots and ensure `axes` is always 2D
        fig, axes = plt.subplots(
            self.num_channels,
            len(num_sources),
            figsize=(6.5, 6),
            constrained_layout=True,
            squeeze=False,  # Ensure axes is always a 2D array
        )
        fig.patch.set_facecolor("white")
        fig.patch.set_alpha(0.0)

        for i, channel in enumerate(self.channels):
            for p, components in enumerate(num_sources):
                all_music = []
                time_vector = None

                for k in range(int(self.num_meas)):
                    music = self.meas_processor.get_music(k, channel, components)
                    if time_vector is None:
                        time_vector = music[0] * 10**9  # Convert to nanoseconds

                    music_current = 20 * np.log10(abs(music[1] ** 2))
                    music_current -= np.max(music_current)  # Normalize
                    all_music.append(music_current)

                    peaks_ind = scipy.signal.find_peaks(music_current, height=[-50, 5])[0]
                    peaks_ind = peaks_ind[peaks_ind >= 150]

                    # Ensure peaks are found before plotting
                    """ 
                    if len(peaks_ind) > 0:
                        axes[i, p].scatter(
                            time_vector[peaks_ind[0]],
                            music_current[peaks_ind[0]],
                            color="green",
                        )
                    if len(peaks_ind) > 1:
                        axes[i, p].scatter(
                            time_vector[peaks_ind[1]],
                            music_current[peaks_ind[1]],
                            color="red",
                        )
                    else:
                        logger.warning(f"Not enough peaks found for channel {i}, measurement {p}")
                    """

                # Convert to array for stats
                all_music = np.array(all_music)
                channel_std = np.std(all_music, axis=0)
                channel_avg = np.average(all_music, axis=0)

                # Plot average trace
                axes[i, p].plot(
                    time_vector,
                    channel_avg,
                    self.linestyles[0],
                    color=self.colors_ch[i],
                    label="Average",
                )

                # Identify and annotate peaks
                peaks, _ = signal.find_peaks(channel_avg, height=-80)
                ls = ["o", "X"]
                for j, peak in enumerate(peaks):
                    axes[i, p].plot(
                        time_vector[peak],
                        channel_avg[peak],
                        ls[j % len(ls)],
                        color="darkorange",
                        label=f"Peak {j+1}: {time_vector[peak]:.2f}ns",
                    )

                # Fill standard deviation
                axes[i, p].fill_between(
                    time_vector,
                    channel_avg - channel_std,
                    channel_avg + channel_std,
                    color=self.colors_ch[i],
                    alpha=0.2,
                    label="Standard Deviation",
                )

                # Formatting
                axes[i, p].patch.set_facecolor("white")
                axes[i, p].patch.set_alpha(1.0)
                axes[i, p].grid()
                axes[i, p].set_ylim([-80, 5])
                if i == self.num_channels - 1:
                    axes[i, p].set_xlabel(r"Time delay $\tau$ [ns]")
                if p == 0:
                    axes[i, p].set_ylabel(f"Channel {channel + 1} " + r"$h(\tau)$ [dB]")
                else:
                    axes[i, p].set_yticklabels([])
                axes[i, p].set_title(f"Number of sources: {components}")
                axes[i, p].legend(fontsize="small")

        # Save the figure
        fig.suptitle(f"MUSIC Spectrum for {self.measurement_name}", fontsize=16)
        fig.savefig(f"{self.save_path}/music_spectrum_{self.measurement_name}.svg")
        fig.savefig(
            f"{self.save_path}/music_spectrum_{self.measurement_name}.png",
            dpi=400,
        )


    def plot_position(self):
        # Set up figure and axis
        fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), constrained_layout=True)
        ax.set_title(f"Distance estimated using MUSIC\nMeasurement {self.measurement_name}")
        x_min, x_max, y_min, y_max = 0, 10, 0, 6

        # Plot room boundaries
        ax.fill_between([x_min - 3, x_max + 3], y_max, y_max + 3, color="lightgray", alpha=0.5)
        ax.fill_between([x_min - 3, x_max + 3], y_min - 3, y_min, color="lightgray", alpha=0.5)
        ax.fill_betweenx([y_min, y_max], x_max, x_max + 3, color="lightgray", alpha=0.5)
        ax.fill_betweenx([y_min, y_max], x_min - 3, x_min, color="lightgray", alpha=0.5)
        
        ax.axhline(y=y_min, color="dimgray", linestyle="--")
        ax.axhline(y=y_max, color="dimgray", linestyle="--")
        ax.axvline(x=x_min, color="dimgray", linestyle="--")
        ax.axvline(x=x_max, color="dimgray", linestyle="--")

        # Plot object and devices
        if "empty" not in self.measurement_name:
            # Define line length
            line_length = 0.6
            half_length = line_length / 2

            # Get the object position (x, y)
            x_obj, y_obj = self.object_pos

            # Calculate start and end points for the 45-degree line
            # At 45 degrees, the x and y offsets are equal
            x_start = x_obj - half_length
            y_start = y_obj + half_length
            x_end = x_obj + half_length
            y_end = y_obj - half_length

            # Plot a tilted line at the object's position
            ax.plot(
                [x_start, x_end],  # x-coordinates of the line
                [y_start, y_end],  # y-coordinates of the line
                lw=4,  # Line width
                color="black",  # Line color
                label=f"Object: {self.measurement_name}"  # Legend label
            )


        for p, color in enumerate(self.colors_devices):
            ax.plot(
                *self.devices_pos[:, p], "o", color=color, label=f"Device {p+1}"
            )
        # Plot ellipses for device pairs
        device_pairs = self.devices
        ellipses = []
        LOSs = []
        for r, (p1, p2) in enumerate(device_pairs):
            x1, y1 = self.devices_pos[:, p1]
            x2, y2 = self.devices_pos[:, p2]
            LOSs.append(np.sqrt((x2-x1)**2+(y2-y1)**2))
            dist_los = np.sqrt((x2-x1)**2+(y2-y1)**2)
            dist_to_obj_1 = np.linalg.norm(self.object_pos - [x1, y1])
            dist_to_obj_2 = np.linalg.norm(self.object_pos - [x2, y2])
            dist_refl = dist_to_obj_1 + dist_to_obj_2
            ellipse = generate_ellipse_param([x1, y1], [x2, y2], dist_refl)
            #if "empty" not in self.measurement_name:
                #plot_ellipse(ax, [ellipse], self.colors_ch[r], self.linestyles[1])
                #ax.plot(x1, x2, linestyle=self.linestyles[1], color=self.colors_ch[r], label=f"Ch{self.channels[r]} measured\nLOS:{dist_los:.2f}m Refl.:{dist_refl:.2f}m")
            ellipses.append(ellipse)
        # Find and plot intersection
        intersection = find_closest_intersection(ellipses)
        #ax.plot(
        #    *intersection, "ro", markersize=10,
        #    label=f"Intersection measured\n({intersection[0]:.2f}, {intersection[1]:.2f})"
        #)



        save_path = f"{self.save_path}/position_{self.measurement_name}.csv"
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['i', 'mean_avg_peaks_0', 'std_avg_peaks_0', 'mean_avg_peaks_1', 'std_avg_peaks_1', 'mean_diff'])


        # Plot MUSIC-based reflections
        fig_hist, ax_hist = plt.subplots(1, 3, figsize=(10,3), layout="constrained")
        fig_hist.suptitle(f'Histogram of Distances - {self.measurement_name}')
        
        channel_ellipses = []
        for i, channel in enumerate(self.channels):
            all_distances = []
            all_peaks = np.zeros((self.num_meas, 2))  # Predefine as 2D array for consistent shape
            est_los = []
            est_refl = []
            # Collect all distances for the histogram
            all_histogram_distances = []

            for k in range(self.num_meas):
                peaks = self.meas_processor.get_music_peaks(k, channel, num_sources=3)
                distance = 0
                if peaks.shape[0] >= 2:
                    tau_e = peaks[1] - peaks[0]
                    distance = LOSs[i] + tau_e

                # Pad `peaks` to ensure length-2 and add to `all_peaks`
                padded_peaks = np.pad(peaks[:2], (0, max(0, 2 - len(peaks))), constant_values=0)
                all_peaks[k] = padded_peaks
                all_distances.append(distance)

                # Append LOS and reflector values if available
                if padded_peaks[0] != 0:
                    est_los.append(padded_peaks[0])
                if padded_peaks[1] != 0:
                    est_refl.append(padded_peaks[1])

            # Filter out zero and NaN distances
            distances_nonzero = np.array(all_distances)[(np.array(all_distances) != 0) & ~np.isnan(all_distances)]
            if distances_nonzero.size == 0:
                continue

            # Add distances to the histogram list
            all_histogram_distances.extend(distances_nonzero)
            if (i == 2) & ('reflector' in self.measurement_name):
                logger.info(f"distances_nonzero: {distances_nonzero}")

            avg_distance = distances_nonzero.mean()

            # Remove rows in `all_peaks` where both values are 0
            valid_peaks = all_peaks[~np.all(all_peaks == 0, axis=1)]

            # Calculate statistics for LOS and reflector peaks
            if valid_peaks.size > 0:
                avg_los = np.mean(est_los) if est_los else 0
                std_los = np.std(est_los) if est_los else 0
                avg_refl = np.mean(est_refl) if est_refl else 0
                std_refl = np.std(est_refl) if est_refl else 0
            else:
                avg_los, std_los, avg_refl, std_refl = 0, 0, 0, 0

            logger.info(f"Channel {i}: Avg LOS = {avg_los:.2f}, Std LOS = {std_los:.3f}, Avg Reflector = {avg_refl:.3f}, Std Reflector = {std_refl:.3f}")

            # Write results to CSV
            with open(save_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                avg_diff = round(avg_refl - avg_los, 2) if avg_los and avg_refl else "N/A"

                # Write row to CSV
                writer.writerow([
                    i,
                    round(avg_los, 2) if avg_los else "N/A",
                    round(std_los, 2) if std_los else "N/A",
                    round(avg_refl, 2) if avg_refl else "N/A",
                    round(std_refl, 2) if std_refl else "N/A",
                    avg_diff,
                ])

            
            bin_edges = np.linspace(0, 10, 41)
            from matplotlib.ticker import AutoMinorLocator
            ax_hist[i].hist(all_histogram_distances, bins=bin_edges, color=self.colors_ch[i], alpha=0.7, edgecolor='black')
            ax_hist[i].set_title(f"Channel {i+1}")
            ax_hist[i].set_xlabel('Distance [m]')
            ax_hist[i].set_ylabel('Frequency')
            ax_hist[i].grid(
                which="major",
                linestyle="-",
                linewidth="0.8",
                color="darkgray",
                alpha=0.8,
            )
            ax_hist[i].grid(
                which="minor",
                linestyle=":",
                linewidth="0.5",
                color="gray",
                alpha=0.7,
            )
            ax_hist[i].xaxis.set_minor_locator(AutoMinorLocator(5))
            ax_hist[i].yaxis.set_minor_locator(AutoMinorLocator(5))
            ax_hist[i].set_xlim([3, 10])
            ax_hist[i].set_ylim([0, 22])

            #logger.info(f"avg_peaks: {avg_peaks}")
            device_pairs = np.roll(np.array(self.devices), 2, axis=0)
            colors_ch = np.roll(np.array(self.colors_ch),  2, axis=0)
            
            #logger.info(f"device_pairs: {device_pairs}")
            focal_1, focal_2 = self.devices_pos[:, device_pairs[i, 0]], self.devices_pos[:, device_pairs[i, 1]]
            #logger.info(f"focal pts: {focal_1}, {focal_2}")
            try:
                ellipse = generate_ellipse_param(focal_1, focal_2, avg_distance)
                channel_ellipses.append(ellipse)
                plot_ellipse(ax, [ellipse], colors_ch[i], self.linestyles[0])
                ax.plot(
                    ellipse[0], ellipse[1], self.linestyles[0],
                    color=colors_ch[i], label=f"Ch{(channel+1)%3 + 1} \nRefl. total distance:{avg_distance:.2f}m"
                    )
            except ValueError as e:
                logger.warning(f"Skipping ellipse for channel {i}: {e}")
                
        # Save the histogram
        histogram_path = f"{self.save_path}/distance_histogram_{self.measurement_name}"
        fig_hist.savefig(histogram_path + ".png")
        fig_hist.savefig(histogram_path + ".svg")

        # Final intersection for MUSIC reflections
        if channel_ellipses:
            print(f"len(channel_ellipses): {len(channel_ellipses)}")
            intersection = find_closest_intersection(channel_ellipses)
            ax.plot(
                *intersection, "rx", markersize=10,
                label=f"Intersection\n({intersection[0]:.2f}, {intersection[1]:.2f})"
            )

        # Configure plot aesthetics
        ax.set_xlim([-1, 11])
        ax.set_ylim([-2, 7])
        ax.set_xlabel("x-axis [m]")
        ax.set_ylabel("y-axis [m]")
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax.grid(which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7)
        ax.minorticks_on()
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=10)
        ax.set_aspect("equal")
        fig.patch.set_facecolor("white")
        ax.patch.set_facecolor("white")

        # Save the figure
        try:
            save_path = f"{self.save_path}/position_{self.measurement_name}"
            fig.savefig(save_path + ".svg", bbox_inches="tight", pad_inches=0.0)
            fig.savefig(save_path + ".png", dpi=400, bbox_inches="tight", pad_inches=0.0)
        except Exception as e:
            logger.warning(f"Could not save plot: {e}")


    def plot_position_compare_real(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
        ax.set_title(
            f"Distance estimated using MUSIC\nMeasurement {self.measurement_name}"
        )
        device_pairs = list(combinations(range(self.devices_pos.shape[1]), 2))
        logger.info(f"Device pairs: {device_pairs}")

        plot_room_boundaries = True
        if plot_room_boundaries:
            # Define the room boundaries
            x_min, x_max = 0, 10
            y_min, y_max = 0, 6

            # Fill outside the horizontal boundaries
            ax.fill_between(
                [x_min - 3, x_max + 3],  # X range for the shaded area
                y_max,  # Bottom y-boundary
                y_max + 3,  # Top y-boundary (outside the room)
                color="lightgray",
                alpha=0.5,
            )
            ax.fill_between(
                [x_min - 3, x_max + 3],
                y_min - 3,  # Bottom y-boundary (outside the room)
                y_min,
                color="lightgray",
                alpha=0.5,
            )

            # Fill outside the vertical boundaries
            ax.fill_betweenx(
                [y_min, y_max],  # Y range for the shaded area
                x_max,  # Left x-boundary
                x_max + 3,  # Right x-boundary (outside the room)
                color="lightgray",
                alpha=0.5,
            )
            ax.fill_betweenx(
                [y_min, y_max],
                x_min - 3,  # Left x-boundary (outside the room)
                x_min,
                color="lightgray",
                alpha=0.5,
            )

            # Add the room boundaries as lines
            ax.axhline(y_min, color="dimgray", linestyle="--")
            ax.axhline(y_max, color="dimgray", linestyle="--")
            ax.axvline(x_min, color="dimgray", linestyle="--")
            ax.axvline(x_max, color="dimgray", linestyle="--")

        # Plot object and devices
        if self.measurement_name != "empty" and self.measurement_name != "empty_2":
            ax.plot(
                self.object_pos[0],
                self.object_pos[1],
                "X",
                lw=20,
                color="black",
                label=f"Object: {self.measurement_name}",
            )
        for p, color in enumerate(self.colors_devices):
            ax.plot(
                self.devices_pos[0, p],
                self.devices_pos[1, p],
                "o",
                color=color,
                label=f"Device {p+1}",
            )

        # Annotate distances between devices

        measured_distances = []
        for r, (p1, p2) in enumerate(device_pairs):
            x1, y1 = self.devices_pos[:, p1]
            x2, y2 = self.devices_pos[:, p2]
            dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            dist_los = dist
            measured_distances.append(dist)

            dist_to_obj_1 = np.sqrt(
                (self.object_pos[0] - x1) ** 2 + (self.object_pos[1] - y1) ** 2
            )

            dist_to_obj_2 = np.sqrt(
                (self.object_pos[0] - x2) ** 2 + (self.object_pos[1] - y2) ** 2
            )

            dist = dist_to_obj_1 + dist_to_obj_2
            dist_refl = dist
            focal_1 = np.array([x1, y1])
            focal_2 = np.array([x2, y2])
            # Calculate ellipse parameters
            center = (focal_1 + focal_2) / 2
            direction = focal_1 - focal_2
            semi_major = dist / 2

            # Validate semi-major and eccentricity
            if semi_major <= np.linalg.norm(direction) / 2:
                logger.warning(
                    f"Channel {r}: Invalid semi-major or direction, skipping ellipse."
                )
                continue

            eccentricity = min(
                (np.linalg.norm(direction) / 2) / semi_major, 1 - 1e-6
            )  # Ensure valid range
            semi_minor = semi_major * np.sqrt(1 - eccentricity**2)
            angle_deg = np.rad2deg(np.arctan2(direction[1], direction[0]))

            # Draw ellipse
            ellipse = patches.Ellipse(
                center,
                width=2 * semi_major,
                height=2 * semi_minor,
                angle=angle_deg,
                edgecolor=self.colors_ch[r - 1],
                facecolor="none",
                linestyle=self.linestyles[1],
                linewidth=2,
            )
            ax.add_patch(ellipse)

            ax.plot(
                center[0],
                center[1],
                self.linestyles[1],
                color=self.colors_ch[r],
                label=f"Ch{r+1} measured \nLOS={dist_los:.2f}m \nReflection={dist_refl:.2f}m",
            )

        measured_distances = np.roll(measured_distances, 2)
        for i, channel in enumerate(self.channels):
            all_distances, all_peaks = [], []
            for k in range(int(self.num_meas)):
                distance = self.meas_processor.get_distance_reflection(k, channel)

                # if channel == 1:
                #    distance = 8.9
                # logger.info(f"Distance: {distance}")
                fetched_peaks = self.meas_processor.get_music_peaks(k, channel)
                logger.info(f"Fetched peaks: {fetched_peaks}")
                distance = distance - (abs(measured_distances[i] - fetched_peaks[0]))
                # distance /= 1.2
                logger.info(f"{measured_distances[i]/fetched_peaks[0]}")

                if len(fetched_peaks) == 0:
                    peaks = np.zeros(2)  # Initialize with zeros if no peaks found
                else:
                    peaks = np.pad(
                        fetched_peaks[:2],
                        (0, max(0, 2 - len(fetched_peaks))),
                        constant_values=0,
                    )
                all_distances.append(distance)
                all_peaks.append(peaks)  # This should have shape (self.num_meas, 2)

            all_distances = np.array(all_distances, dtype=np.float64)
            all_peaks = np.array(all_peaks)
            distances_nonzero = all_distances[
                (all_distances != 0) & (~np.isnan(all_distances))
            ]
            # logger.info(f"Distances_nonzero: {distances_nonzero}")
            if distances_nonzero.size == 0:
                continue

            all_peaks = all_peaks[~np.any(all_peaks == 0, axis=1)]
            # logger.info(f"All peaks: {all_peaks}")

            # logger.info(f"all_peaks.shape {np.array(all_peaks).shape}")
            avg_distance = np.average(distances_nonzero)
            avg_peaks = np.average(all_peaks, axis=0)

            # logger.info(f"Device pos: {self.devices_pos}")
            # logger.info(f"Devices: {self.devices}")

            # Validate device indices
            if max(np.array(self.devices[i])) >= self.devices_pos.shape[1]:
                raise IndexError(
                    f"Invalid device index in self.devices[{i}]: {self.devices[i]} exceeds the size of devices_pos ({self.devices_pos.shape[1]})."
                )

            # logger.info(f"Devices: {self.devices[channel][:]}")
            # logger.info(f"Devices pos: { self.devices_pos}")
            # logger.info(f"{self.devices_pos[:, self.devices[channel][0]]}")
            focal_1, focal_2 = (
                self.devices_pos[:, self.devices[channel][0]],
                self.devices_pos[:, self.devices[channel][1]],
            )
            # logger.info(f"Focals: {focal_1} and {focal_2}")

            # Calculate ellipse parameters
            center = (focal_1 + focal_2) / 2
            direction = focal_1 - focal_2
            semi_major = avg_distance / 2

            # Validate semi-major and eccentricity
            if semi_major <= np.linalg.norm(direction) / 2:
                logger.warning(
                    f"Channel {i}: Invalid semi-major or direction, skipping ellipse."
                )
                continue

            eccentricity = min(
                (np.linalg.norm(direction) / 2) / semi_major, 1 - 1e-6
            )  # Ensure valid range
            semi_minor = semi_major * np.sqrt(1 - eccentricity**2)
            angle_deg = np.rad2deg(np.arctan2(direction[1], direction[0]))

            # Draw ellipse
            ellipse = patches.Ellipse(
                center,
                width=2 * semi_major,
                height=2 * semi_minor,
                angle=angle_deg,
                edgecolor=self.colors_ch[i],
                facecolor="none",
                linestyle=self.linestyles[0],
                linewidth=2,
            )
            ax.add_patch(ellipse)
            ax.plot(
                center[0],
                center[1],
                self.linestyles[0],
                color=self.colors_ch[i],
                label=f"Ch{i+1} estimated\nLOS={avg_peaks[0]:.2f}m \nReflection={avg_peaks[1]:.2f}m",
            )

        # Finalize plot
        ax.set_xlim([-1, 11])
        ax.set_ylim([-2, 7])
        ax.set_xlabel("x-axis [m]")
        ax.set_ylabel("y-axis [m]")
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax.grid(which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7)

        ax.minorticks_on()

        ax.legend(
            loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=10
        )
        ax.set_aspect("equal")

        fig.patch.set_facecolor("white")
        fig.patch.set_alpha(0.0)

        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(1.0)

        try:
            save_path = f"{self.save_path}/position_compare_{self.measurement_name}"
            fig.savefig(save_path + ".svg", bbox_inches="tight", pad_inches=0.0)
            fig.savefig(
                save_path + ".png", dpi=400, bbox_inches="tight", pad_inches=0.0
            )
        except Exception as e:
            logger.warning(f"Could not save plot: {e}")

    def plot_measurement_setup(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
        ax.set_title(f"Measurement Setup Anechoic Chamber")
        device_pairs = list(combinations(range(self.devices_pos.shape[1]), 2))
        # logger.info(f"Device pairs: {device_pairs}")
        """
        plot_room_boundaries = True
        if plot_room_boundaries:
            # Define the room boundaries
            x_min, x_max = 0, 10
            y_min, y_max = 0, 6

            # Fill outside the horizontal boundaries
            ax.fill_between(
                [x_min-3, x_max+3],
                y_max, y_max + 3,
                color="lightgray", alpha=0.5
            )
            ax.fill_between(
                [x_min-3, x_max+3],
                y_min - 3, y_min,
                color="lightgray", alpha=0.5
            )

            # Fill outside the vertical boundaries
            ax.fill_betweenx(
                [y_min, y_max],
                x_max, x_max + 3,
                color="lightgray", alpha=0.5
            )
            ax.fill_betweenx(
                [y_min, y_max],
                x_min - 3, x_min,
                color="lightgray", alpha=0.5
            )

            # Add the room boundaries as lines
            ax.axhline(y_min, color="dimgray", linestyle="--")
            ax.axhline(y_max, color="dimgray", linestyle="--")
            ax.axvline(x_min, color="dimgray", linestyle="--")
            ax.axvline(x_max, color="dimgray", linestyle="--")
            
        """
        # Plot object and devices
        ax.plot(
            self.object_pos[0],
            self.object_pos[1],
            "X",
            lw=20,
            color="black",
        )

        ax.text(
            self.object_pos[0] - 0.2,
            self.object_pos[1] - 0.4,
            "Object",
            fontsize=10,
            color="black",
        )

        for p, color in enumerate(self.colors_devices):
            ax.plot(
                self.devices_pos[0, p],
                self.devices_pos[1, p],
                "o",
                color=color,
            )
            ax.text(
                self.devices_pos[0, p] + 0.3,
                self.devices_pos[1, p] + 0.1,
                f"D{p+1}",
                fontsize=10,
                color=color,
            )

        # Annotate distances between devices
        for r, (p1, p2) in enumerate(self.devices):
            x1, y1 = self.devices_pos[:, p1]
            x2, y2 = self.devices_pos[:, p2]
            dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            ax.plot(
                [x1, x2],
                [y1, y2],
                linestyle="--",
                color=self.colors_ch[self.channels[r]],
                linewidth=3,
                alpha=1,
                label=f"Ch {self.channels[r]+1}= {dist:.2f}m",
            )
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(
                mid_x,
                mid_y,
                f"Ch. {self.channels[r]+1}",
                fontsize=9,
                color=self.colors_ch[self.channels[r]],
                ha="center",
                bbox=dict(
                    facecolor="white", edgecolor="none", alpha=0.99
                ),  # White rectangle
            )

        # Annotate distances to object
        for p in range(self.devices_pos.shape[1]):
            x_dev, y_dev = self.devices_pos[:, p]
            dist_to_obj = np.sqrt(
                (self.object_pos[0] - x_dev) ** 2 + (self.object_pos[1] - y_dev) ** 2
            )
            ax.plot(
                [x_dev, self.object_pos[0]],
                [y_dev, self.object_pos[1]],
                linestyle="--",
                color=self.colors_ch[self.channels[p]],
                linewidth=3,
                alpha=0.5,
                label=f"{dist_to_obj:.2f}m",
            )
            mid_x, mid_y = (x_dev + self.object_pos[0]) / 2, (
                y_dev + self.object_pos[1]
            ) / 2 + 0.1

        # Finalize plot
        
        """
        ax.set_xlim([-1, 11])
        ax.set_ylim([-1, 7])
        """
        
        ax.set_xlim([1.5, 9])
        ax.set_ylim([1, 3.5])
        ax.set_xlabel("x-axis [m]")
        ax.set_ylabel("y-axis [m]")
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax.grid(which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7)

        ax.minorticks_on()
        ax.set_aspect("equal")

        fig.patch.set_facecolor("white")
        fig.patch.set_alpha(0.0)

        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(1.0)
        ax.legend(loc="lower right")

        fig.savefig(
            self.save_path + "measurement_setup.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.0,
        )
        fig.savefig(
            self.save_path + "measurement_setup.svg",
            bbox_inches="tight",
            pad_inches=0.0,
        )

    def plot_music_error(self, num_sources):
        fig, ax = plt.subplots(2, 3, figsize=(12, 6), layout="constrained")
        for channel in self.channels:
            e_los_arr, e_refl_arr = [], []
            for num_source in num_sources:
                los, refl = 0, 0  # Init values
                music_peaks = self.meas_processor.get_music_peaks(
                    index=1, channel=channel, num_sources=num_source
                )

                if len(music_peaks) >= 1:
                    los = music_peaks[0]
                    if len(music_peaks) >= 2:
                        refl = music_peaks[1]

                # Calc true distance los
                p1, p2 = self.devices[channel][0], self.devices[channel][1]
                x1, y1 = self.devices_pos[:, p1]
                x2, y2 = self.devices_pos[:, p2]
                channel_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                e_los = RMSE(y_est=los, y_true=channel_length)
                e_los_arr.append(e_los)
                # logger.info(f"e_los: {e_los}")
                # Calc distance to object (reflection path)
                x1, y1 = self.devices_pos[:, p1]
                x2, y2 = self.devices_pos[:, p2]
                dist_to_obj_1 = np.sqrt(
                    (self.object_pos[0] - x1) ** 2 + (self.object_pos[1] - y1) ** 2
                )
                dist_to_obj_2 = np.sqrt(
                    (self.object_pos[0] - x2) ** 2 + (self.object_pos[1] - y2) ** 2
                )
                e_refl = RMSE(y_est=refl, y_true=dist_to_obj_1 + dist_to_obj_2)
                e_refl_arr.append(e_refl)
                # logger.info(f"e_refl: {e_refl}")

            # For the first stem plot
            markerline1, stemlines1, baseline1 = ax[0, channel].stem(
                num_sources,
                e_los_arr,
                linefmt=f"{self.colors_ch[channel]}",
                markerfmt="o",
                basefmt=f"{self.colors_ch[channel]}",
                label="Error LOS",
            )
            # Set the linewidth to 2 for stemlines
            plt.setp(stemlines1, linewidth=4)

            # Customize the rest of the first plot
            ax[0, channel].set_xlabel("Number of sources in MUSIC")
            ax[0, channel].set_ylabel("RMSE")
            ax[0, channel].set_title(f"Channel {channel+1} LOS")
            ax[0, channel].set_ylim([0, 1.2])
            ax[0, channel].grid()

            # For the second stem plot
            markerline2, stemlines2, baseline2 = ax[1, channel].stem(
                num_sources,
                e_refl_arr,
                linefmt=f"{self.colors_ch[channel]}",
                markerfmt="o",
                basefmt=f"{self.colors_ch[channel]}",
                label="Error Reflection",
            )
            # Set the linewidth to 2 for stemlines
            plt.setp(stemlines2, linewidth=4)

            # Customize the rest of the second plot
            ax[1, channel].set_xlabel("Number of sources in MUSIC")
            ax[1, channel].set_ylabel("RMSE")
            ax[1, channel].set_title(f"Channel {channel+1} Reflection")
            ax[1, channel].set_ylim([0, 10])
            ax[1, channel].grid()

        fig.savefig(
            self.save_path + f"music_error_{self.measurement_name}.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.0,
        )
        fig.savefig(
            self.save_path + f"music_error_{self.measurement_name}.svg",
            bbox_inches="tight",
            pad_inches=0.0,
        )


    def snr(self):
        fig, ax = plt.subplots(1, len(self.channels), figsize=(10, 3.5), constrained_layout=True)
        fig.suptitle(f"Frequency spectrum '{self.measurement_name}'")
        if len(self.channels) == 1:
            ax = [ax]
        fig_rssi, ax_rssi = plt.subplots(1,1, figsize=(6, 4.5), layout="constrained")
        # File path for saving the CSV
        csv_file_path = os.path.join(self.save_path, f"rssi_means_{self.measurement_name}.csv")

        with open(csv_file_path, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["channel", "local", "std_local", "remote", "std_remote"])
        for i, channel in enumerate(self.channels):
            all_IQ = [
                (
                    self.meas_processor.get_IQ(idx_meas)[channel][0]
                    + 1j * self.meas_processor.get_IQ(idx_meas)[channel][1]
                )[4:-4]
                * (
                    self.meas_processor.get_IQ(idx_meas)[channel][2]
                    + 1j * self.meas_processor.get_IQ(idx_meas)[channel][3]
                )[4:-4]
                for idx_meas in range(int(self.num_meas))
            ]

            if not all_IQ or len(all_IQ[0]) == 0:
                logger.error(f"No valid IQ data for channel {channel}")
                continue

            
            time_vector = (
                np.linspace(0, 1 / self.fs * len(all_IQ[0]), len(all_IQ[0])) * 10**6
            )
            IQ_avg = np.average(all_IQ, axis=0)
        
            IQ_std = np.std(all_IQ, axis=0)


            if np.all(IQ_avg == 0):
                logger.error(f"Zeroed IQ_avg for channel {channel}")
                
            # Compute the FFT spectrum
            s = np.fft.fft(IQ_avg, n=512)
            s = 20 * np.log10(abs(s))
            s = s - np.max(s)  # Normalize the spectrum
            s = np.fft.fftshift(s)
            # Frequency axis setup
            f = np.fft.fftfreq(512, d=1/self.fs)/(10**6)  # Frequency axis in Hz
            f = np.fft.fftshift(f)  # Shift frequencies to center at 0 Hz


            # Find peaks in the spectrum
            peaks, _ = scipy.signal.find_peaks(s)

            # Identify the maximum peak (signal)
            peak_max_index = peaks[np.argmax(s[peaks])]
            peak_max_value = s[peak_max_index]

            # Find the index of the maximum peak
            peak_max_index = np.argmax(s)

            # Define the ±1 MHz range
            freq_range = 1  # MHz

            # Find indices corresponding to ±1 MHz around the peak
            freq_range_indices = np.where(np.abs(f - f[peak_max_index]) <= freq_range)[0]

            # Exclude the peak and its immediate surroundings (e.g., ±100 kHz)
            peak_exclusion = 0.1  # MHz
            peak_exclusion_indices = np.where(np.abs(f - f[peak_max_index]) <= peak_exclusion)[0]

            # Create the noise region by excluding the peak area from the ±1 MHz range
            noise_region = np.setdiff1d(freq_range_indices, peak_exclusion_indices)

            # Calculate average noise power
            average_rest = np.mean(s[noise_region])

            # Calculate SNR (assuming s is in dB)
            ratio = s[peak_max_index] - average_rest
            
            # Plotting
            ax[i].plot(f, s, color=self.colors_ch[i])
            ax[i].axhline(average_rest, color="tab:red", linestyle="--", label=rf"$N_\text{{avg}}$ = {average_rest:.1f} dB")
            ax[i].plot(f[peak_max_index], s[peak_max_index], 'o', color="tab:red", 
                    label=rf"$f$ = {f[peak_max_index]:.3f} MHz")

            # Add axis labels
            ax[i].set_xlabel("Frequency (MHz)")
            ax[i].set_ylabel("Amplitude (dB)")
            ax[i].set_title(f"Channel {i+1}\nSNR = {ratio:.1f} dB")
            ax[i].set_xlim([-self.fs/4*10**(-6), self.fs/4*10**(-6)])
            ax[i].set_ylim([-70, 2])
            ax[i].legend(loc="lower left")
            ax[i].grid()

            
            
            # Collect RSSI data
            rssi_remote_arr = []
            rssi_local_arr = []
            txpwr_local_arr = []
            txpwr_remote_arr = []
            
            for meas in range(self.num_meas):
                rssi_local_arr.append((-1)*self.meas_processor.get_distance(meas)['rssi_local'][i])   
                rssi_remote_arr.append((-1)*self.meas_processor.get_distance(meas)['rssi_remote'][i]) 
                txpwr_local_arr.append(self.meas_processor.get_distance(meas)['txpwr_local'][i])   
                txpwr_remote_arr.append(self.meas_processor.get_distance(meas)['txpwr_remote'][i]) 

            
            # Compute the mean RSSI values
            mean_rssi_local = np.mean(rssi_local_arr)
            mean_rssi_remote = np.mean(rssi_remote_arr)

            std_rssi_local = np.std(rssi_local_arr)
            std_rssi_remote = np.std(rssi_remote_arr)

            # Save the means to a CSV
            with open(csv_file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)

                # Write data
                writer.writerow([i, f"{mean_rssi_local:.2f}", f"{std_rssi_local:.2f}", f"{mean_rssi_remote:.2f}", f"{std_rssi_remote:.2f}"])

            print(f"Saved mean RSSI values to {csv_file_path}")

            # Continue with existing plotting and saving code...
            ax_rssi.set_title(f"RSSI - {self.measurement_name}")

            # Plotting...
            ax_rssi.axhline(
                mean_rssi_local, color=self.colors_ch[i], linestyle="-", 
                label=f"Mean Local = {mean_rssi_local:.0f} dBm"
            )
            ax_rssi.axhline(
                mean_rssi_remote, color=self.colors_ch[i], linestyle="--", 
                label=f"Mean Remote = {mean_rssi_remote:.0f} dBm"
            )
            ax_rssi.grid()
            ax_rssi.set_ylim([-60, -37])  # Adjust based on actual data
            ax_rssi.set_xlabel("Measurement Index")
            ax_rssi.set_ylabel("RSSI [dBm]")
            ax_rssi.legend(loc="lower right")

        fig.savefig(
            self.save_path + f"snr_{self.measurement_name}.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.0,
        )

        fig.savefig(
            self.save_path + f"snr_{self.measurement_name}.svg",
            bbox_inches="tight",
            pad_inches=0.0,
        )

        fig_rssi.savefig(
            self.save_path + f"rssi_{self.measurement_name}.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.0,
        )

        fig_rssi.savefig(
            self.save_path + f"rssi_{self.measurement_name}.svg",
            bbox_inches="tight",
            pad_inches=0.0,
        )

    def plot(self):
        #self.plot_constellation()
        #self.plot_time()
        #self.plot_transfer()
        #self.plot_impulse_ifft()
        #self.plot_impulse_music(num_sources=[2])
        #self.plot_position()
        #self.plot_position_compare_real()
        #self.plot_measurement_setup()
        #self.plot_music_error(num_sources=[1,2,3,4,5])
        self.snr()