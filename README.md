[![Build Status](https://travis-ci.com/dsa110/dsa110-antpos.svg?branch=casa-dev)](https://travis-ci.com/dsa110/dsa110-antpos)
[![codecov](https://codecov.io/gh/dsa110/dsa110-antpos/branch/casa-dev/graph/badge.svg)](https://codecov.io/gh/dsa110/dsa110-antpos)

# dsa110-antpos

Antenna positions as CSV file and a python script to read and return lat/long for each station.

## Installation

```
pip install -r requirements.txt
pip install .
```

Requires astropy, numpy, pandas.

## To use

The functions in utils allow manipulation of the antennas list, as well as a calculation of the days per frb detection.

The scripts in the scripts dir can be used to simulate MSs in CASA and image them.
