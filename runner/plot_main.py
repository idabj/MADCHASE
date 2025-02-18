from plotter import MeasurementPlotter
import numpy as np
import matplotlib.pyplot as plt

CH1, CH2, CH3 = 0, 1, 2
I_LOCAL, Q_LOCAL, I_REMOTE, Q_REMOTE = 0, 1, 2, 3

# Example usage:
BASE_DIR = "measurements/"

# Tina sine: devices_pos = [ 
# 1.88   7      5.10;  % x
# 2.25   2.25   0.74;  % y
# 2      2      2      % z
#]; %1      2      3
devices_pos = np.array(         # row0 = x pos, row1 = y pos
    [[1.88, 7,5.10], [2.25, 2.25, 0.74]] #D1, D3, D2
)

#devices_pos = np.array(         # row0 = x pos, row1 = y pos
#    [[1.88,5.10, 7], [2.25, 0.74, 2.25]]
#)

devices_pos[0,:] += 1
devices_pos[1,:] += 2

save_folder_path = "/home/ida/Documents/obsidian/00 Prosjektoppgåve/Fordypningsprosjekt/figures/measurements/"
measurement_names = ["empty", "empty_2", "reflector", "reflector_rotate", "scatter"]
measurement_name = measurement_names[2]
colors_ch = ["yellowgreen", "tab:blue", "darkorange"]
colors_devices = ["teal", "steelblue", "slateblue"]

# NTNU colors
#colors_ch = ["#D5DF7C", "#9DB7E1", "#F4AC67"]
#colors_devices = ["#7C8934", "#3E628A", "#90552A"]
for measurement_name in measurement_names:
    plotter = MeasurementPlotter(BASE_DIR, save_folder_path, measurement_name, colors_ch, colors_devices)
    plotter.plot()
    
# Compare transfer functions for empty and reflection
measurement_names = ["empty_2", "reflector_rotate"]
#measurement_names = ["reflector", "scatter"]
measurement_names = ["empty", "empty_2", "reflector","reflector_rotate", "scatter"]

fig, ax = plt.subplots(3,2, figsize=(8,8),layout="constrained") #figsize=(width, height)
fig.patch.set_facecolor('white')
fig.patch.set_alpha(0.0)

for i, channel in enumerate(plotter.channels):
    for p, components in enumerate([1, 2]):
        all_measurement_data = []  # To store data from all measurements for comparison
        time_vector = None

        for measurement_name in measurement_names:  # Loop over measurements
            plotter = MeasurementPlotter(BASE_DIR, save_folder_path, measurement_name, colors_ch, colors_devices)
            all_music = []

            for k in range(int(plotter.num_meas)):
                music = plotter.meas_processor.get_music(k, channel, components)
                if time_vector is None:
                    time_vector = music[0] * 10**9  # Convert to nanoseconds

                music_current = 20 * np.log10(abs(music[1] ** 2))
                music_current -= np.max(music_current)  # Normalize
                all_music.append(music_current)

            # Convert to array for stats
            all_music = np.array(all_music)
            channel_std = np.std(all_music, axis=0)
            channel_avg = np.average(all_music, axis=0)

            # Save data for later comparison
            all_measurement_data.append((channel_avg, channel_std, measurement_name))
            

        # Plot data from all measurements on the same axes
        for j, (channel_avg, channel_std, measurement_name) in enumerate(all_measurement_data):
            # Use a different linestyle or color for each measurement
            color = plotter.colors_ch[i]
            linestyle = ["-", "--", ":"][j % 3]  # Cycle through styles if needed
            ax[i, p].plot(
                time_vector,
                channel_avg,
                linestyle,
                color=color,
                label=f"{measurement_name}",
            )

        # Formatting and annotation
        ax[i, p].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
        ax[i, p].grid(
            which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
        )

        ax[i, p].minorticks_on()
        ax[i, p].patch.set_facecolor('white')
        ax[i, p].patch.set_alpha(1.0)
        
        ax[i, p].set_ylim([-80, 5])
        if i == plotter.num_channels - 1:
            ax[i, p].set_xlabel(r"Time delay $\tau$ [ns]")
        if p == 0:
            ax[i, p].set_ylabel(f"Channel {channel + 1}" + r"$h(\tau)$ [dB]")
        else:
            ax[i, p].set_yticklabels([])
        ax[i, p].set_title(f"Number of sources: {components}")
        ax[i, p].legend(fontsize="small")
        
save_name = save_folder_path + f"music_comparison_"
for measurement_name in measurement_names:
    save_name += f"{measurement_name}_"
    
fig.savefig(save_name + ".png", dpi=400)
fig.savefig(save_name + ".svg")
    
    
    
    
    
fig, ax = plt.subplots(3, 1, figsize=(4, 8), layout="constrained")  # Create subplots
fig.patch.set_facecolor('white')
fig.patch.set_alpha(0.0)

for i, channel in enumerate(plotter.channels):
    all_measurement_data = []  # Store transfer function data for all measurements

    for measurement_name in measurement_names:  # Loop over measurements
        plotter = MeasurementPlotter(BASE_DIR, save_folder_path, measurement_name, colors_ch, colors_devices)
        all_transfers = []
        frequency_vector = None

        for k in range(int(plotter.num_meas)):  # Loop over individual measurements
            frequency_vector, transfer, phase = plotter.meas_processor.get_transfer(k, channel)
            if frequency_vector is None:
                frequency_vector = frequency_vector * 1e9  # Convert to nanoseconds if necessary

            transfer_db = 20 * np.log10(abs(transfer))
            transfer_db -= np.max(transfer_db)  # Normalize
            all_transfers.append(transfer_db)

        # Convert to array for statistics
        all_transfers = np.array(all_transfers)
        channel_std = np.std(all_transfers, axis=0)
        channel_avg = np.average(all_transfers, axis=0)

        # Save the average and standard deviation for later comparison
        all_measurement_data.append((channel_avg, channel_std, measurement_name))

    # Plot the data for all measurements on the same axes
    for j, (channel_avg, channel_std, measurement_name) in enumerate(all_measurement_data):
        linestyle = ["-", "--", ":"][j % 3]  # Cycle through styles
        color = plotter.colors_ch[i]
        ax[i].plot(
            frequency_vector,
            channel_avg,
            linestyle,
            color=color,
            label=f"{measurement_name}",
        )
        ax[i].fill_between(
            frequency_vector,
            channel_avg - channel_std,
            channel_avg + channel_std,
            color=color,
            alpha=0.2,
        )

    ax[i].set_ylim([-5,0.5])
    # Formatting and annotation
    ax[i].grid(which="major", linestyle="-", linewidth="0.5", color="gray")
    ax[i].grid(
        which="minor", linestyle=":", linewidth="0.5", color="gray", alpha=0.7
    )
    ax[i].minorticks_on()
    ax[i].patch.set_facecolor('white')
    ax[i].patch.set_alpha(1.0)

    ax[i].set_xlabel(r"Frequency [MHz]")
    ax[i].set_ylabel(f"Channel {channel + 1}" + r"$H(f)$ [dB]")
    ax[i].set_title(f"Channel {channel + 1} Transfer Function")
    ax[i].legend(fontsize="small")

save_name = save_folder_path + f"transfer_comparison_"
for measurement_name in measurement_names:
    save_name += f"{measurement_name}_"

# Save the figure
fig.savefig(save_name + ".png", dpi=400)
fig.savefig(save_name + ".svg")