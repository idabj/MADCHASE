
# MaDChaSE
This repository contain software for perfoming channel estimation using three nRF52833 Development kits (DK) and a PC. The firmware for the DKs are in `iq_sampler\`and the software performing and analysing the measurements are in `runner\`. 

## Runner
Python script that starts the measurement procedure and stores the result in timestamped folders. Each measurement are processed the same way.

```mermaid
graph LR;
    A[Set roles for measurement] --> B;
    B[Perform measurement] --> C;
    C[Save JSON] --> D;
    D[Plot results];
```

| Measurement/Roles | DK1       | DK2       | DK3       |
|-------------------|-----------|-----------|-----------|
| Channel 1         | reflector | initiator | none      |
| Channel 2         | none      | reflector | initiator |
| Channel 3         | initiator | none      | reflector |

```mermaid
flowchart LR;
    A(DK1);
    B(DK2);
    C(DK3);

    A<--ch1-->B;
    B<--ch2-->C;
    C<--ch3-->A;
```


### Setting up the environment
Make virtual environment for python in the folder `runner/` and install necessary packages.
```shell
python3 -m venv env
```

```shell
source env/bin/activate
```

```shell
pip install -r requirements.txt
```

### Measure
Run `main.py`, this sends a message to the initiator over uart which tells it to start a measurement. The results are then sent with uart to the laptop. The script then saves the data to json, and plots. Each measurement with its files are saved into separate folders by timestamp. Both reflector and initiator must be connected to the laptop with USB.

<!---
### Create `requirements.txt`
```shell
pip install pipreqs
```

```shell
pipreqs .
```
This command must be run in the `runner\` directory.
-->

### Files 

| **File**        | **Description**                                                                                                                                                |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `algorithms.py` | MUSIC algorithm for estimating the impulse response.                                                                                                           |
| `api.py`        | Class for reading measurements from the file system (after measuring).                                                                                         |
| `client.py`     | Used for organizing the measurement cycle, sets the roles of the devices and saves the data from each measurement.                                             |
| `ellipse.py`    | Functions for calculating ellipses, used for plotting and localization.                                                                                        |
| `main.py`       | Script for taking the measurements, input argument with name of the measurement. The measurements are saved to a folder with the same name as the measurement. |
| `plot_main.py`  | Creates and saves plots for specified measurements.                                                                                                            |
| `plotter.py`    | Class for plotting the data, transfer function, impulse response etc.                                                                                          |

## IQ Sampler
Firmware for the DKs. Reads UART for roles, then performs the measurements.


### Development
Follow this guide https://docs.nordicsemi.com/bundle/ncs-2.4.3/page/nrf/getting_started/installing.html for installing the SDK and toolchain.

SDK: v2.7.0

Toolchain: v2.7.0

Add the correct SIDs to the Makefile. Then build and flash within `iq_sampler\`. Make sure to connect all devices before running the command, or alter the command.

```shell
make first && make flash1 && make flash2 && make flash3
```