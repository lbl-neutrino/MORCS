# Mx2x2 Overall Run Control Software

## Installing

Do this on e.g. `acd-ops01` as the `acdaq` user.

``` bash
git clone --recurse-submodules https://github.com/mjkramer/MORCS.git
cd MORCS
python -m venv morcs.venv
source morcs.venv/bin/activate
pip install -e .
```

## Loading

``` bash
source /path/to/MORCS/morcs.venv/bin/activate
```

## Configuring

Edit `morcs.toml` under `[crs]` to specify the hostname of the CRS DAQ server (e.g. `acd-daq02`) and the paths to `crs_daq`, its virtual environment, and the output and log directories. Likewise, under `[lrs]` the `host` should be set appropriately.

## Starting and stopping a run

``` bash
morcs start-run
```

``` bash
morcs stop-run
```

## Run database

Run information is stored in `morcs.sqlite`. Currently only the run number, start time, and end time are stored. Run numbers are generated automatically, starting from zero.

## Current status

The CRS controller has been tested in a mock environment. The LRS controller needs to be updated to use the new Flask API. Both the LRS and MINERvA controllers need to be updated following recent changes to `DaqController`, and the run number needs to be propagated.
