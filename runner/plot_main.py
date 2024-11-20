from plotter import MeasurementPlotter
import numpy as np

CH1, CH2, CH3 = 0, 1, 2
I_LOCAL, Q_LOCAL, I_REMOTE, Q_REMOTE = 0, 1, 2, 3

# Example usage:
BASE_DIR = "measurements/"
devices_pos = np.array(         # row0 = x pos, row1 = y pos
    [[1.88, 5.10, 7], [2.25, 0.74, 2.25]]
)  
save_folder_path = "/home/ida/Documents/obsidian/00 Prosjektoppgåve/Fordypningsprosjekt/figures/measurements/"
measurement_names = ["empty", "empty_2", "reflector", "reflector_rotate", "scatter"]
measurement_name = measurement_names[2]
colors_ch = ["tab:green", "tab:blue", "tab:red"]
colors_devices = ["#F57942", "#4550F5", "#93F566"]

for measurement_name in measurement_names:
    plotter = MeasurementPlotter(BASE_DIR, save_folder_path, measurement_name, colors_ch, colors_devices)
    plotter.plot()