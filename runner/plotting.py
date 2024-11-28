from api import *
from itertools import combinations

def plot_constellation(
    BASE_DIR, measurement_name, colors=["tab:blue", "tab:green", "tab:red"]
):
    # Create a figure with 3 subplots, one for each channel
    fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
    fig.suptitle(f"Constellation Plots for Measurement '{measurement_name}'")

    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3

    channels = [0, 1, 2]  # CH1, CH2, CH3
    devices = [(1, 3), (3, 2), (2, 1)]

    for i, channel in enumerate(channels):
        # Plot constellation for each measurement in the channel
        for k in range(int(num_meas)):
            iq_data = meas_processor.get_IQ(k)[
                channel
            ]  # Get I/Q data for the given channel

            # Extract the I and Q components (i_local, q_local, i_remote, q_remote)
            i_local = iq_data[0]
            q_local = iq_data[1]

            i_remote = iq_data[2]
            q_remote = iq_data[3]

            # Plot the I/Q data on the constellation plot
            ax[1, i].scatter(
                i_local, q_local, color=colors[i], s=5, alpha=0.2
            )  # scatter plot for the local I/Q
            ax[0, i].scatter(
                i_remote, q_remote, color=colors[i], s=5, alpha=0.2
            )  # scatter plot for the local I/Q

        # Customize the plot for this channel
        ax[0, i].set_xlabel("In-Phase (I)")
        ax[0, i].set_ylabel("Quadrature (Q)")
        ax[0, i].set_title(f"Channel {channel + 1} Local\nDevice {devices[channel][0]}")
        ax[0, i].set_aspect("equal")  # To make sure the axes have the same scale
        ax[0, i].set_xlim([-9000, 9000])
        ax[0, i].set_ylim([-9000, 9000])
        ax[0, i].grid(True)

        ax[1, i].set_xlabel("In-Phase (I)")
        ax[1, i].set_ylabel("Quadrature (Q)")
        ax[1, i].set_title(
            f"Channel {channel + 1} Remote\nDevice {devices[channel][1]}"
        )
        ax[1, i].set_aspect("equal")  # To make sure the axes have the same scale
        ax[1, i].set_xlim([-9000, 9000])
        ax[1, i].set_ylim([-9000, 9000])
        ax[1, i].grid(True)

    # Save the figure
    fig.savefig(save_folder_path + f"constellation_{measurement_name}.svg")
    fig.savefig(save_folder_path + f"constellation_{measurement_name}.png", dpi=400)


def plot_time_domain(
    BASE_DIR, measurement_name, colors=["tab:blue", "tab:green", "tab:red"]
):
    # Create a figure with 3 subplots, one for each channel
    fig, ax = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
    fig.suptitle(f"Constellation Plots for Measurement '{measurement_name}'")

    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3

    channels = [0, 1, 2]  # CH1, CH2, CH3

    for i, channel in enumerate(channels):
        # Plot constellation for each measurement in the channel
        for k in range(int(num_meas)):
            iq_data = meas_processor.get_IQ(k)[
                channel
            ]  # Get I/Q data for the given channel

            # Extract the I and Q components (i_local, q_local, i_remote, q_remote)
            i_local = iq_data[0]
            q_local = iq_data[1]
            local = i_local + 1j * q_local

            i_remote = iq_data[2]
            q_remote = iq_data[3]
            remote = i_remote + 1j * q_remote
            logger.info(f"Shape remote signal: {remote.shape}")
            fs = 1e6
            time_vector = np.linspace(0, 1 / fs * len(remote), len(remote)) * 10**6

            # Plot the I/Q data on the constellation plot
            ax[1, i].plot(time_vector, local, color=colors[i], alpha=0.5)
            ax[0, i].plot(time_vector, remote, color=colors[i], alpha=0.5)
            # ax[1,i].stem(time_vector, local, linefmt=colors[i], markerfmt=colors[i], basefmt=" ")
            # ax[0,i].stem(time_vector, remote, linefmt=colors[i], markerfmt=colors[i], basefmt=" ")

        # Customize the plot for this channel
        ax[1, i].set_xlabel("Time (ms)")
        ax[1, i].set_ylabel("Magnitude")
        ax[1, i].set_title(f"Channel {channel + 1} Local")
        ax[1, i].grid(True)
        ax[1, i].set_xlim([5, 10])

        ax[0, i].set_xlabel("Time (ms)")
        ax[0, i].set_ylabel("Magnitude")
        ax[0, i].set_title(f"Channel {channel + 1} Remote")
        ax[0, i].grid(True)
        ax[0, i].set_xlim([5, 10])

    # Save the figure
    fig.savefig(save_folder_path + f"time_domain_{measurement_name}.svg")
    fig.savefig(save_folder_path + f"time_domain_{measurement_name}.png", dpi=400)


def plot_transfer(
    BASE_DIR,
    measurement_name,
    linestyles=["-", "--"],
    colors=["tab:blue", "tab:green", "tab:red"],
):
    fig, ax = plt.subplots(3, 2, figsize=(12, 12), constrained_layout=True)
    fig.suptitle(f"Measurement '{measurement_name}'")
    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3

    channels = [0, 1, 2]  # CH1, CH2, CH3

    for i, channel in enumerate(channels):
        channel_avg_mag = np.zeros_like(meas_processor.get_transfer(0, channel)[1])
        channel_avg_phase = np.zeros_like(meas_processor.get_transfer(0, channel)[2])
        all_transfers_mag = []
        all_transfers_phase = []
        frequency_vector = None

        for k in range(int(num_meas)):
            frequency, transfer_mag, transfer_phase = meas_processor.get_transfer(
                k, channel
            )
            if frequency_vector is None:
                frequency_vector = frequency

            transfer_mag_db = 20 * np.log10(abs(transfer_mag / np.max(transfer_mag)))
            transfer_mag_db = transfer_mag_db - np.max(transfer_mag_db)
            all_transfers_mag.append(transfer_mag_db)
            all_transfers_phase.append(transfer_phase)

            # Plot individual measurements in gray
            ax[i, 0].plot(
                frequency_vector * 10 ** (-6),
                transfer_mag_db,
                linestyles[1],
                color="gray",
                alpha=0.2,
            )
            ax[i, 1].plot(
                frequency_vector * 10 ** (-6),
                transfer_phase,
                linestyles[1],
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
            color=colors[i],
            label="Average",
        )
        ax[i, 0].fill_between(
            frequency_vector * 10 ** (-6),
            (channel_avg_mag - channel_std_mag),
            (channel_avg_mag + channel_std_mag),
            color=colors[i],
            alpha=0.2,
            label="Standard Deviation",
        )

        # Plot phase
        ax[i, 1].plot(
            frequency_vector * 10 ** (-6),
            channel_avg_phase,
            color=colors[i],
            label="Average",
        )
        ax[i, 1].fill_between(
            frequency_vector * 10 ** (-6),
            (channel_avg_phase - channel_std_phase),
            (channel_avg_phase + channel_std_phase),
            color=colors[i],
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
    fig.savefig(save_folder_path + f"transfer_{measurement_name}.svg")
    fig.savefig(save_folder_path + f"transfer_{measurement_name}.png", dpi=400)
    


def plot_impulse(
    BASE_DIR,
    measurement_name,
    linestyles=["-", "--"],
    colors=["tab:blue", "tab:green", "tab:red"],
):
    fig, ax = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True)
    fig.suptitle(f"Measurement '{measurement_name}'")
    meas_processor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(meas_processor.folder.list_files()) / 3

    channels = [0, 1, 2]  # CH1, CH2, CH3

    for i, channel in enumerate(channels):
        all_impulses = []
        time_vector = None

        for k in range(int(num_meas)):
            impulse = meas_processor.get_impulse(k, channel)
            # transfer = meas_processor.get_transfer(k, channel)[1]
            # impulse = music(2)
            if time_vector is None:
                time_vector = (
                    impulse[0] * 10**9
                )  # Set the reference time vector from the first measurement

            impulse_current = 20 * np.log10(abs(impulse[1] / np.max(impulse[1])) ** 2)
            impulse_current = impulse_current - np.max(impulse_current)
            all_impulses.append(impulse_current)  # Collect the impulse data

            # Plot individual measurements in gray
            ax[i].plot(
                time_vector, impulse_current, linestyles[1], color="gray", alpha=0.2
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
        ax[i].plot(time_vector, channel_avg, color=colors[i], label=f"Average")

        # Plot the peak point
        ax[i].plot(
            peak_time,
            peak_value,
            "o",
            color=colors[i],
            label=f"Peak: {abs(peak_time):.2f}ns",
        )

        # Plot the standard deviation as a shaded region around the average
        ax[i].fill_between(
            time_vector,
            (channel_avg - channel_std),
            (channel_avg + channel_std),
            color=colors[i],
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
    fig.savefig(save_folder_path + f"impulse_{measurement_name}.svg")
    fig.savefig(save_folder_path + f"impulse_{measurement_name}.png", dpi=400)
    


def plot_object(ax, object_pos, measurement_name):
    ax.plot(
        object_pos[0],
        object_pos[1],
        "X",
        lw=20,
        color="black",
        label=f"Object: {measurement_name}",
    )


def plot_devices(ax, devices_pos, colors_devices):
    for p in range(devices_pos.shape[1]):
        ax.plot(
            devices_pos[0, p],
            devices_pos[1, p],
            "o",
            color=colors_devices[p],
            label=f"Device {p+1}",
        )


def annotate_distances_between_devices(ax, devices_pos, device_pairs, colors_ch):
    for r, (p1, p2) in enumerate(device_pairs):
        x1, y1 = devices_pos[:, p1]
        x2, y2 = devices_pos[:, p2]
        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.annotate(
            f"{distance:.2f}m", (mid_x, mid_y), color="black", fontsize=10, ha="center"
        )
        ax.plot([x1, x2], [y1, y2], linestyle="--", color=colors_ch[r - 1], alpha=0.5)


def annotate_distances_to_object(ax, devices_pos, object_pos):
    for p in range(devices_pos.shape[1]):
        x_dev, y_dev = devices_pos[:, p]
        x_obj, y_obj = object_pos
        distance_to_object = np.sqrt((x_obj - x_dev) ** 2 + (y_obj - y_dev) ** 2)
        mid_x, mid_y = (x_dev + x_obj) / 2, (y_dev + y_obj) / 2
        ax.annotate(
            f"{distance_to_object:.2f}m",
            (mid_x, mid_y),
            color="black",
            fontsize=10,
            ha="center",
        )
        ax.plot([x_dev, x_obj], [y_dev, y_obj], linestyle="--", color="gray", alpha=0.5)


def calculate_ellipse_parameters(center, direction_vector, distance_avg):
    semi_major = distance_avg / 2
    linear_eccentricity = (np.linalg.norm(direction_vector) / 2) / semi_major
    if linear_eccentricity >= 1:
        return None
    semi_minor = semi_major * np.sqrt(1 - linear_eccentricity**2)
    angle = np.arctan2(direction_vector[1], direction_vector[0])
    return semi_major, semi_minor, np.rad2deg(angle)


def add_ellipse(
    ax, center, semi_major, semi_minor, angle_deg, edge_color, linestyle, alpha=1
):
    ellipse = patches.Ellipse(
        center,
        width=2 * semi_major,
        height=2 * semi_minor,
        angle=angle_deg,
        edgecolor=edge_color,
        facecolor="none",
        linestyle=linestyle,
        linewidth=2,
        alpha=alpha,
    )
    ax.add_patch(ellipse)


def process_channel_data(
    ax,
    measprocessor,
    num_meas,
    channels,
    devices_pos,
    linestyles,
    colors,
    channel_devices,
):
    for i, channel in enumerate(channels):
        all_distances, all_peaks = [], []
        for k in range(int(num_meas)):
            distance = measprocessor.get_distance_reflector(k, channel)
            peaks = measprocessor.get_music_peaks(k, channel)
            all_distances.append(distance)
            peaks = np.pad(peaks[:2], (0, max(0, 2 - len(peaks))), constant_values=0)
            all_peaks.append(peaks)

        all_distances = np.array(all_distances, dtype=np.float64)
        all_peaks = np.array(all_peaks)
        all_distances_nonzero = all_distances[
            (all_distances != 0) & (~np.isnan(all_distances))
        ]
        all_peaks_nonzero = all_peaks[
            :, ~((all_peaks == 0) | np.isnan(all_peaks)).any(axis=0)
        ]

        if all_distances_nonzero.size == 0:
            continue

        distance_avg = np.average(all_distances_nonzero)
        peaks_avg = np.average(all_peaks, axis=0)
        focal_point_1 = devices_pos[:, channel_devices[i][0]]
        focal_point_2 = devices_pos[:, channel_devices[i][1]]
        center = (focal_point_1 + focal_point_2) / 2
        direction_vector = focal_point_1 - focal_point_2

        params = calculate_ellipse_parameters(center, direction_vector, distance_avg)
        if params:
            semi_major, semi_minor, angle_deg = params
            add_ellipse(
                ax, center, semi_major, semi_minor, angle_deg, colors[i], linestyles[0]
            )
            ax.plot(
                center[0],
                center[1],
                linestyles[0],
                color=colors[i],
                label=f"Ch{i+1} \nLOS={peaks_avg[0]:.2f}m \nReflection={peaks_avg[1]:.2f}m",
            )


def plot_position(
    BASE_DIR,
    measurement_name,
    devices_pos,
    linestyles=["-", ":"],
    colors=["tab:blue", "tab:green", "tab:red"],
    colors_devices=["pink", "purple", "goldenrod"],
):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
    measprocessor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(measprocessor.folder.list_files()) / 3
    channels = [0, 1, 2]
    device_pairs = list(combinations(range(devices_pos.shape[1]), 2))
    channel_devices = [(0, 2), (2, 1), (1, 0)]
    object_pos = np.array([1.7, 0.74])

    plot_object(ax, object_pos, measurement_name)
    plot_devices(ax, devices_pos, colors_devices)
    annotate_distances_between_devices(ax, devices_pos, device_pairs, colors)
    annotate_distances_to_object(ax, devices_pos, object_pos)
    process_channel_data(
        ax,
        measprocessor,
        num_meas,
        channels,
        devices_pos,
        linestyles,
        colors,
        channel_devices,
    )

    ax.set_xlabel("x-axis [m]")
    ax.set_ylabel("y-axis [m]")
    ax.grid()
    ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
    ax.set_aspect("equal", "box")

    try:
        fig.savefig(save_folder_path + f"position_{measurement_name}.svg")
        fig.savefig(f"{save_folder_path}/position_{measurement_name}.png", dpi=400)
    except Exception as e:
        logger.warning(f"Could not save plot: {e}")


def plot_music(
    BASE_DIR,
    measurement_name,
    num_sources=[1, 2, 3, 4],
    linestyles=["-", "--"],
    colors=["tab:blue", "tab:green", "tab:red"],
):
    """
    Plots MUSIC spectra for multiple channels and component configurations.

    Args:
        BASE_DIR (str): Base directory containing measurement data.
        measurement_name (str): Name of the measurement to process.
        save_folder_path (str): Path to save the generated plot.
        num_sources (list): List of component values to evaluate.
        linestyles (list): List of line styles for average and individual traces.
        colors (list): List of colors for each channel.

    Returns:
        None: Saves the figure to the specified path.
    """
    num_channels = 3
    fig, axes = plt.subplots(
        num_channels, len(num_sources), figsize=(16, 10), constrained_layout=True
    )

    measprocessor = MeasurementProcessor(BASE_DIR, measurement_name)
    num_meas = len(measprocessor.folder.list_files()) // 3

    channels = [0, 1, 2]  # CH1, CH2, CH3

    for i, channel in enumerate(channels):
        for p, components in enumerate(num_sources):
            all_music = []
            time_vector = None

            for k in range(int(num_meas)):
                music = measprocessor.get_music(k, channel, components)
                if time_vector is None:
                    time_vector = music[0] * 10**9  # Convert to nanoseconds

                music_current = 20 * np.log10(abs(music[1] ** 2))
                music_current -= np.max(music_current)  # Normalize
                all_music.append(music_current)

                # Plot individual traces
                axes[i, p].plot(
                    time_vector, music_current, linestyles[1], color="gray", alpha=0.2
                )

            # Convert to array for stats
            all_music = np.array(all_music)
            channel_std = np.std(all_music, axis=0)
            channel_avg = np.average(all_music, axis=0)

            # Plot average trace
            axes[i, p].plot(
                time_vector,
                channel_avg,
                linestyles[0],
                color=colors[i],
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
                color=colors[i],
                alpha=0.2,
                label="Standard Deviation",
            )

            # Formatting
            axes[i, p].grid()
            axes[i, p].set_ylim([-80, 5])
            if i == num_channels - 1:
                axes[i, p].set_xlabel(r"Time delay $\tau$ [ns]")
            if p == 0:
                axes[i, p].set_ylabel(f"Channel {channel + 1}" + r"$h(\tau)$ [dB]")
            axes[i, p].set_title(f"Number of sources: {components}")
            axes[i, p].legend(fontsize="small")

    # Save the figure
    fig.suptitle(f"MUSIC Spectrum for {measurement_name}", fontsize=16)
    fig.savefig(f"{save_folder_path}/music_spectrum_{measurement_name}.svg")
    fig.savefig(f"{save_folder_path}/music_spectrum_{measurement_name}.png", dpi=400)


CH1, CH2, CH3 = 0, 1, 2
I_LOCAL, Q_LOCAL, I_REMOTE, Q_REMOTE = 0, 1, 2, 3

# Example usage:
BASE_DIR = "measurements/"
measurement_data = [("empty", 8), ("reflector_rotate_2", 3)]

devices_pos = np.array(         # row0 = x pos, row1 = y pos
    [[1.88, 5.10, 7], [2.25, 0.74, 2.25]]
)  
save_folder_path = "/home/ida/Documents/obsidian/00 Prosjektoppgåve/Fordypningsprosjekt/figures/measurements/"
# plot_impulse_responses(BASE_DIR, measurement_data)
measurement_names = ["empty", "empty_2", "reflector", "reflector_rotate", "scatter"]
measurement_name = measurement_names[1]
colors_ch = ["tab:red", "tab:green", "tab:blue"]
colors_devices = ["#F57942", "#4550F5", "#93F566"]
for measurement_name in measurement_names:
    plot_time_domain(BASE_DIR, measurement_name, colors = colors_ch)
    plot_transfer(BASE_DIR, measurement_name, colors = colors_ch)
    plot_impulse(BASE_DIR, measurement_name, colors = colors_ch)
    plot_constellation(BASE_DIR, measurement_name, colors = colors_ch)
    plot_music(BASE_DIR, measurement_name, num_sources=[1, 2, 3, 4], colors=colors_ch)
    plot_position(
        BASE_DIR,
        measurement_name,
        devices_pos,
        colors=colors_ch,
        colors_devices=colors_devices,
    )