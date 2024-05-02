# Mx2x2 Overall Run Control Software

## Requirements

On AL9 run `dnf install python3-devel krb5-devel`. Kerberos is needed for the SSH connection to the CRS DAQ server.

## Installing

Do this on e.g. `acd-ops01` as the `acdaq` user.

``` bash
git clone --recurse-submodules https://github.com/mjkramer/MORCS.git
cd MORCS
python -m venv morcs.venv
source morcs.venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

## Loading

``` bash
source /path/to/MORCS/morcs.venv/bin/activate
```

It may be necessary to set up a pair of SSH tunnels to the MINERvA DAQ, e.g.:

``` bash
ssh -L 1090:localhost:1090 -R 9998:localhost:9998 acd-mnv03
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

The CRS and LRS controllers have been tested. The MINERvA controller needs to be updated following recent changes to `DaqController`, and the run number needs to be propagated.
