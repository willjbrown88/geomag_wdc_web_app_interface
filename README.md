[![Build Status](https://travis-ci.org/lbillingham/geomag_wdc_web_app_interface.svg?branch=master)](https://travis-ci.org/lbillingham/geomag_wdc_web_app_interface)

# geomag_wdc_web_app_interface
programmatically get data from http://wdc.bgs.ac.uk/dataportal/
installable like: `pip install git+https://github.com/willjbrown88/geomag_wdc_web_app_interface.git`

Very much a work in progress, building towards version 1.0 release. Currently master branch will build and run as intended for a user.

Main function for getting data is `consume_webservices.fetch_data`.

## Example usage:
```python
from datetime import date
from lib import consume_webservices as cws

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
`tests/functional_tests.test_fetch_data_wdc_format_hour_data_from_wdc`
for detailed useage.
This will download all available hourly data housed in the WDC for Geomagnetism, Edinburgh, for dates between `start_date` and `end_date`, from 'ESK'(dalemuir) and 'LER'(wick) observatories, to the directory '/tmp/'.

## MagPySV
Designed to support observatory secular variation data processing work of Grace Cox in `MagPySV` (see [Grace's GitHub repo](https://github.com/gracecox/MagPySV/)), which will install this project as a dependecy to fetch WDC data on demand.
