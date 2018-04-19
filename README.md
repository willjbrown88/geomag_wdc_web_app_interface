# gmdata_webinterface
[![Build Status](https://travis-ci.org/willjbrown88/geomag_wdc_web_app_interface.svg?branch=master)](https://travis-ci.org/willjbrown88/geomag_wdc_web_app_interface)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

This Python package allows a users to programmatically download data from the
[British Geological Survey (BGS) Data Portal to the World Data Centre (WDC)
for geomagnetism, Edinburgh](http://wdc.bgs.ac.uk/dataportal/).

Currently hour and minute cadence WDC files from geomagnetic observatories
can be downloaded in this manner.

This code was originally developed by Laurence Billingham, and is now maintained
by William Brown.

### MagPySV
This package was designed in part to support observatory secular variation data processing work
of Grace Cox in `MagPySV` (see [Grace's GitHub repo](https://github.com/gracecox/MagPySV/)),
which will install this project as a dependecy to fetch WDC data on demand.

## Installation
The latest official release of the package can be installed from the Python Package
Index PyPI with
`pip install gmdata_webinterface`.

The latest working version of the package can also be installed directly from git with:
`pip install git+https://github.com/willjbrown88/geomag_wdc_web_app_interface.git`

## Usage
The main function for getting data is `consume_webservices.fetch_data()`.

### Example usage:
```python
from datetime import date
from gmdata_webinterface import consume_webservices as cws

cadence = 'hour'
stations = ['ESK', 'LER']
start_date = date(2015, 4, 1)
end_date = date(2015, 4, 30)
service = 'WDC'
download_dir = '/tmp/'
cws.fetch_data(
        start_date=start_date, end_date=end_date,
        station_list=stations, cadence=cadence,
        service=service, saveroot=download_dir
)
```
See the docstring on `fetch_data` and the test in
`gmdata_webinterface/tests/functional_tests.test_fetch_data_wdc_format_hour_data_from_wdc`
for detailed useage.
This will download all available hourly data housed in the WDC for Geomagnetism,
Edinburgh, for dates between `start_date` and `end_date`, from 'ESK'(dalemuir) and
'LER'(wick) observatories, to the directory '/tmp/'.

## Contributing
This is a working project, with open source under an MIT license. You can report
bugs, suggest changes, and contribute to this project via github at
https://github.com/willjbrown88/geomag_wdc_web_app_interface.

Expansion of the current package to access other ground observatory data services,
such as INTERMAGNET and the AUX_OBS_ product of the ESA Swarm mission, are currently
being developed. Any contributions or suggestion are welcome.

### Source code install
You can obtain the source code from github with e.g.:
`git clone https://github.com/willjbrown88/geomag_wdc_web_app_interface.git ./my_source_dir/`
The code can then be built, documented and tested in various ways with the make `make` command,
when in the source code directory.
Type `make help` in the source directory to see the available options, e.g.

  * To install the package from source use:
    `make install`

  * To install in editable, development mode use:
    `make develop`

  * To run the unit tests:
    `make test`

  * To build the html documentation:
    `make docs`

## Reference
A manuscript describing [MagPySV](https://github.com/gracecox/MagPySV) and the
intergated functionality of this package is currently in preparation.

While the project is open source, we ask that you abide by the included MIT license,
and acknowledge the authors where due.
