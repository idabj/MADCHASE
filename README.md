
## RUNNER
Make virtual environment for python in the folder runner/ and install necessary packages.
```shell
python3 -m venv env
```

```shell
source env/bin/activate
```

```shell
pip install -r requirements.txt
```

Run `main.py`, this sends a message to the initiator over uart which tells it to start a measurement. The results are then sent with uart to the laptop. The script then saves the data to json, and plots. Each measurement with its files are saved into separate folders by timestamp. Both reflector and initiator must be connected to the laptop with USB.

### Create `requirements.txt`
```shell
pip install pipreqs
```

```shell
pipreqs .
```
This command must be run in the `runner\` directory.
