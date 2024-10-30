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

### Create `requirements.txt`
```shell
pip install pipreqs
```

```shell
pipreqs .
```
This command must be run in the `runner\` directory.
