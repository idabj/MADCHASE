from api import *
from itertools import combinations
import matplotlib.pyplot as plt
import logging

CH1, CH2, CH3 = 0, 1, 2


class MeasurementPlotter:
    def __init__(
        self, BASE_DIR, save_path, measurement_name, colors_ch, colors_devices
    ):
        self.save_path = save_path
        self.meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
        self.measurement_name = measurement_name
        self.num_meas = len(self.meas_processor.folder.list_files()) / 3
        self.channels = [CH1, CH2, CH3]  # CH1, CH2, CH3
        self.num_channels = len(self.channels)
        self.devices = [(0, 2), (2, 1), (1, 0)]
        self.devices_pos = np.array([[1.88, 5.10, 7], [2.25, 0.74, 2.25]])
        self.object_pos = np.array([1.7, 0.74])

        self.linestyles = ["-", "--"]
        self.colors_ch = colors_ch
        self.colors_devices = colors_devices
        self.fs = 4e6

    def plot_constellation(self):
        fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
        fig.suptitle(f"Constellation Plots for Measurement '{self.measurement_name}'")

        for i, channel in enumerate(self.channels):
            for k in range(int(self.num_meas)):
                iq_data = self.meas_processor.get_IQ(k)[channel]

                for j, (i_data, q_data, title_suffix) in enumerate(
                    [
                        (
                            iq_data[0],
                            iq_data[1],
                            f"Local\nDevice {self.devices[channel][0]}",
                        ),
                        (
                            iq_data[2],
                            iq_data[3],
                            f"Remote\nDevice {self.devices[channel][1]}",
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

        save_fig_path = self.save_path + f"constellation_{self.measurement_name}"
        fig.savefig(save_fig_path + ".svg")
        fig.savefig(save_fig_path + ".png", dpi=400)

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
        fig.savefig(save_fig_path + ".png", dpi=400)

    def plot_transfer(self):
        fig, ax = plt.subplots(3, 2, figsize=(12, 12), constrained_layout=True)
        fig.suptitle(f"Measurement '{self.measurement_name}'")

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
                    frequency_vector = frequency

                transfer_mag_db = 20 * np.log10(
                    abs(transfer_mag / np.max(transfer_mag))
                )
                transfer_mag_db = transfer_mag_db - np.max(transfer_mag_db)
                all_transfers_mag.append(transfer_mag_db)
                all_transfers_phase.append(transfer_phase)

                # Plot individual measurements in gray
                ax[i, 0].plot(
                    frequency_vector * 10 ** (-6),
                    transfer_mag_db,
                    self.linestyles[1],
                    color="gray",
                    alpha=0.2,
                )
                ax[i, 1].plot(
                    frequency_vector * 10 ** (-6),
                    transfer_phase,
                    self.linestyles[1],
                    color="gray",
                    alpha=0.2,
                )

            # Convert to numpy arrays
            all_transfers_mag = np.array(all_transfers_mag)
            all_transfers_phase = np.array(all_transfers_phase)

            # Calculate standard deviation and average
            channel_std_mag = np.std(all_transfers_mag, axis=0)
            channel_avg_mag = np.average(all_transfers_mag, axis=0)
            channel_std_phase = np.std(all_transfers_phase, axis=0)
            channel_avg_phase = np.average(all_transfers_phase, axis=0)

            # Plot magnitude
            ax[i, 0].plot(
                frequency_vector * 10 ** (-6),
                channel_avg_mag,
                color=self.colors_ch[i],
                label="Average",
            )
            ax[i, 0].fill_between(
                frequency_vector * 10 ** (-6),
                (channel_avg_mag - channel_std_mag),
                (channel_avg_mag + channel_std_mag),
                color=self.colors_ch[i],
                alpha=0.2,
                label="Standard Deviation",
            )

            # Plot phase
            ax[i, 1].plot(
                frequency_vector * 10 ** (-6),
                channel_avg_phase,
                color=self.colors_ch[i],
                label="Average",
            )
            ax[i, 1].fill_between(
                frequency_vector * 10 ** (-6),
                (channel_avg_phase - channel_std_phase),
                (channel_avg_phase + channel_std_phase),
                color=self.colors_ch[i],
                alpha=0.2,
                label="Standard Deviation",
            )

            # Magnitude plot settings
            ax[i, 0].set_ylim([-5, 0.5])
            ax[i, 0].set_xlabel("Frequency (MHz)")
            ax[i, 0].set_ylabel(r"Magnitude $|H(f)|$ [dB]")
            ax[i, 0].set_title(f"Channel {channel+1} Magnitude")
            ax[i, 0].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            ax[i, 0].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )
            ax[i, 0].minorticks_on()
            ax[i, 0].legend()

            # Phase plot settings
            ax[i, 1].set_ylim([-9, 3])
            ax[i, 1].set_xlabel("Frequency (MHz)")
            ax[i, 1].set_ylabel("Phase [radians]")
            ax[i, 1].set_title(f"Channel {channel+1} Phase")
            ax[i, 1].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            ax[i, 1].grid(
                which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
            )
            ax[i, 1].minorticks_on()
            ax[i, 1].legend()

        # Save the figure
        fig.savefig(self.save_path + f"transfer_{self.measurement_name}.svg")
        fig.savefig(self.save_path + f"transfer_{self.measurement_name}.png", dpi=400)

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
            logger.info(f"All impulses shape: {all_impulses.shape}")

            # Calculate standard deviation for each time point across all measurements
            channel_std = np.std(all_impulses, axis=0)
            channel_avg = np.average(all_impulses, axis=0)
            logger.info(
                f"Channel std: {channel_std.shape} channel avg: {channel_avg.shape}"
            )

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
        fig.savefig(self.save_path + f"impulse_{self.measurement_name}.png", dpi=400)

    def plot_impulse_music(self, num_sources=[1, 2, 3, 4]):
        fig, axes = plt.subplots(
            self.num_channels,
            len(num_sources),
            figsize=(16, 10),
            constrained_layout=True,
        )

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

                    # Plot individual traces
                    axes[i, p].plot(
                        time_vector,
                        music_current,
                        self.linestyles[1],
                        color="gray",
                        alpha=0.2,
                    )

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
                axes[i, p].grid()
                axes[i, p].set_ylim([-80, 5])
                if i == self.num_channels - 1:
                    axes[i, p].set_xlabel(r"Time delay $\tau$ [ns]")
                if p == 0:
                    axes[i, p].set_ylabel(f"Channel {channel + 1}" + r"$h(\tau)$ [dB]")
                axes[i, p].set_title(f"Number of sources: {components}")
                axes[i, p].legend(fontsize="small")

        # Save the figure
        fig.suptitle(f"MUSIC Spectrum for {self.measurement_name}", fontsize=16)
        fig.savefig(f"{self.save_path}/music_spectrum_{self.measurement_name}.svg")
        fig.savefig(
            f"{self.save_path}/music_spectrum_{self.measurement_name}.png", dpi=400
        )

    def plot_position(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
        ax.set_title(f"Distance estimated using MUSIC\nMeasurement {self.measurement_name}")
        device_pairs = list(combinations(range(self.devices_pos.shape[1]), 2))
        logger.info(f"Device pairs: {device_pairs}")
        
        plot_room_boundaries = True
        if plot_room_boundaries:
            # Define the room boundaries
            x_min, x_max = 0, 10
            y_min, y_max = 0, 6
            
            # Fill outside the horizontal boundaries
            ax.fill_between(
                [x_min-3, x_max+3],  # X range for the shaded area
                y_max,           # Bottom y-boundary
                y_max + 3,       # Top y-boundary (outside the room)
                color="lightgray",
                alpha=0.5
            )
            ax.fill_between(
                [x_min-3, x_max+3],
                y_min - 3,       # Bottom y-boundary (outside the room)
                y_min,
                color="lightgray",
                alpha=0.5
            )

            # Fill outside the vertical boundaries
            ax.fill_betweenx(
                [y_min, y_max],  # Y range for the shaded area
                x_max,           # Left x-boundary
                x_max + 3,       # Right x-boundary (outside the room)
                color="lightgray",
                alpha=0.5
            )
            ax.fill_betweenx(
                [y_min, y_max],
                x_min - 3,       # Left x-boundary (outside the room)
                x_min,
                color="lightgray",
                alpha=0.5
            )

            # Add the room boundaries as lines
            ax.axhline(y_min, color="dimgray", linestyle="--")
            ax.axhline(y_max, color="dimgray", linestyle="--")
            ax.axvline(x_min, color="dimgray", linestyle="--")
            ax.axvline(x_max, color="dimgray", linestyle="--")
            
        # Plot object and devices
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
        """
        for r, (p1, p2) in enumerate(device_pairs):
            x1, y1 = self.devices_pos[:, p1]
            x2, y2 = self.devices_pos[:, p2]
            dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            ax.annotate(
                f"{dist:.2f}m",
                ((x1 + x2) / 2, (y1 + y2) / 2),
                color="black",
                fontsize=10,
                ha="center",
            )
            ax.plot(
                [x1, x2],
                [y1, y2],
                linestyle="--",
                color=self.colors_ch[r - 1],
                alpha=0.5,
            )
        
        # Annotate distances to object
        for p in range(self.devices_pos.shape[1]):
            x_dev, y_dev = self.devices_pos[:, p]
            dist_to_obj = np.sqrt(
                (self.object_pos[0] - x_dev) ** 2 + (self.object_pos[1] - y_dev) ** 2
            )
            ax.annotate(
                f"{dist_to_obj:.2f}m",
                ((x_dev + self.object_pos[0]) / 2, (y_dev + self.object_pos[1]) / 2),
                color="black",
                fontsize=10,
                ha="center",
            )
            ax.plot(
                [x_dev, self.object_pos[0]],
                [y_dev, self.object_pos[1]],
                linestyle="--",
                color="gray",
                alpha=0.5,
            )
        """
        for i, channel in enumerate(self.channels):
            all_distances, all_peaks = [], []
            for k in range(int(self.num_meas)):
                distance = self.meas_processor.get_distance_reflector(k, channel)
                fetched_peaks = self.meas_processor.get_music_peaks(k, channel)
                if len(fetched_peaks) == 0:
                    peaks = np.zeros(2)  # Initialize with zeros if no peaks found
                else:
                    peaks = np.pad(
                        fetched_peaks[:2],
                        (0, max(0, 2 - len(fetched_peaks))),
                        constant_values=0,
                    )
                all_distances.append(distance)
                all_peaks.append(peaks)

            all_distances = np.array(all_distances, dtype=np.float64)
            all_peaks = np.array(all_peaks)
            distances_nonzero = all_distances[
                (all_distances != 0) & (~np.isnan(all_distances))
            ]
            logger.info(f"Distances_nonzero: {distances_nonzero}")
            if distances_nonzero.size == 0:
                continue

            avg_distance = np.average(distances_nonzero)
            avg_peaks = np.average(all_peaks, axis=0)

            logger.info(f"Device pos: {self.devices_pos}")
            logger.info(f"Devices: {self.devices}")

            # Validate device indices
            if max(np.array(self.devices[i])) >= self.devices_pos.shape[1]:
                raise IndexError(
                    f"Invalid device index in self.devices[{i}]: {self.devices[i]} exceeds the size of devices_pos ({self.devices_pos.shape[1]})."
                )

            logger.info(f"Devices: {self.devices[i]}")
            focal_1, focal_2 = (
                self.devices_pos[:, self.devices[i][0]],
                self.devices_pos[:, self.devices[i][1]],
            )
            logger.info(f"Focals: {focal_1} and {focal_2}")

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
                label=f"Ch{i+1} \nLOS={avg_peaks[0]:.2f}m \nReflection={avg_peaks[1]:.2f}m",
            )

        # Finalize plot
        ax.set_xlim([-1, 11])
        ax.set_ylim([-2, 7])
        ax.set_xlabel("x-axis [m]")
        ax.set_ylabel("y-axis [m]")
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax.grid(
            which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
        )

        ax.minorticks_on()
        
        ax.legend(
            loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=10
        )
        ax.set_aspect("equal")

        try:
            save_path = f"{self.save_path}/position_{self.measurement_name}"
            fig.savefig(save_path + ".svg", bbox_inches="tight", pad_inches=0.0)
            fig.savefig(save_path + ".png", dpi=400, bbox_inches="tight", pad_inches=0.0)
        except Exception as e:
            logger.warning(f"Could not save plot: {e}")

    def plot_measurement_setup(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
        ax.set_title(f"Measurement Setup Anechoic Chamber")
        device_pairs = list(combinations(range(self.devices_pos.shape[1]), 2))
        logger.info(f"Device pairs: {device_pairs}")
        
        plot_room_boundaries = True
        if plot_room_boundaries:
            # Define the room boundaries
            x_min, x_max = 0, 10
            y_min, y_max = 0, 6
            
            # Fill outside the horizontal boundaries
            ax.fill_between(
                [x_min-3, x_max+3],  # X range for the shaded area
                y_max,           # Bottom y-boundary
                y_max + 3,       # Top y-boundary (outside the room)
                color="lightgray",
                alpha=0.5
            )
            ax.fill_between(
                [x_min-3, x_max+3],
                y_min - 3,       # Bottom y-boundary (outside the room)
                y_min,
                color="lightgray",
                alpha=0.5
            )

            # Fill outside the vertical boundaries
            ax.fill_betweenx(
                [y_min, y_max],  # Y range for the shaded area
                x_max,           # Left x-boundary
                x_max + 3,       # Right x-boundary (outside the room)
                color="lightgray",
                alpha=0.5
            )
            ax.fill_betweenx(
                [y_min, y_max],
                x_min - 3,       # Left x-boundary (outside the room)
                x_min,
                color="lightgray",
                alpha=0.5
            )

            # Add the room boundaries as lines
            ax.axhline(y_min, color="dimgray", linestyle="--")
            ax.axhline(y_max, color="dimgray", linestyle="--")
            ax.axvline(x_min, color="dimgray", linestyle="--")
            ax.axvline(x_max, color="dimgray", linestyle="--")
            
        # Plot object and devices
        ax.plot(
            self.object_pos[0],
            self.object_pos[1],
            "X",
            lw=20,
            color="black",
            label=f"Object",
        )
        for p, color in enumerate(self.colors_devices):
            ax.plot(
                self.devices_pos[0, p],
                self.devices_pos[1, p],
                "o",
                color=color,
                label=f"Device {p+1} (D{p+1})",
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
                alpha=1,
                label = f"Ch. {self.channels[r]+1} = {dist:.2f}m"
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
                alpha=0.5,
                label=f"Obj-D{p+1} = {dist_to_obj:.2f}m"
            )
            
        # Finalize plot
        ax.set_xlim([-1, 11])
        ax.set_ylim([-1, 7])
        ax.set_xlabel("x-axis [m]")
        ax.set_ylabel("y-axis [m]")
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax.grid(
            which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
        )

        ax.minorticks_on()
        
        ax.legend(
            loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=10
        )
        ax.set_aspect("equal")
        
        fig.savefig(self.save_path + "measurement_setup.png", dpi=400, bbox_inches="tight", pad_inches=0.0)
        fig.savefig(self.save_path + "measurement_setup.svg", bbox_inches="tight", pad_inches=0.0)
        
    def plot(self):
        self.plot_constellation()
        self.plot_time()
        self.plot_transfer()
        self.plot_impulse_ifft()
        self.plot_impulse_music()
        self.plot_position()
        self.plot_measurement_setup()
