[![Build Status](https://travis-ci.org/lbillingham/geomag_wdc_web_app_interface.svg?branch=master)](https://travis-ci.org/lbillingham/geomag_wdc_web_app_interface)

# geomag_wdc_web_app_interface
programmatically get data from http://wdc.bgs.ac.uk/dataportal/
installable like: `pip install .`

Main function for getting data is `consume_webservices.fetch_data`.

## Example usage:
```python
from lib import consume_webservices as cws

cadence = 'hour'
station = 'NGK'
start_date = date(2015, 4, 1)
end_date = date(2015, 4, 30)
service = 'WDC'
download_dir = '/tmp/'
configpath = os.path.join(<some_dir>, 'wdc_minute_data_wdcoutput.ini')
cws.fetch_data(
        start_date, end_date,
        station, cadence,
        service, download_dir, configpath
)
```
See the docstring on `fetch_data` and the test in
`tests/functional_tests.test_fetch_data_wdc_format_hour_data_from_wdc`
for detailed useage.



very much a work in progress

# Notes from 2017-01-16 meeting with Grace Cox and Will Brown
Main project is to get a data set of secual variation
rapid core features liek jerks
monthly differences of monthly means

R Holme and Will's thesis have a method for
removing external fields.

Everyone has a different algorithm for calc monthly means and
nobody really says what they do.
There is not even, really, a set of monthly means that gets distributed.
BCMT does give values but they are raw: with external field still apparent.
Will Brown has a script to clean BCMT values based on the supplied record
flags.

Grace's wants a single opensource, reproducible reference implimentation.

Grace's code reads WDC format data
that are hourly and with a daily mean.
Would like to support WDC format as this is the most widely
used format and is what most folk will have already.

from a USB stick into a
folder layout something like (*)

```
singleobservatory
|
|---------NGK
|         |
|         1999, 2000, 2001, ...
|
|---------ESK
|         |
|         1986, 1987, ...
|
...
```
see [Grace's GitHub repo](https://github.com/gracecox/MagPy/tree/master/magpy/data/BGS_hourly/hourval/single_obs)

read into big `DdataFrame` hourly means per observatory from ~1960-present
using `glob`. [Gillet et al., 2015 COV-OBS model](http://www.spacecenter.dk/files/magnetic-models/COV-OBSx1/COV-OBS.x1.pdf) used to subtract the core field.

Denoising step uses `DataFrame` that looks like:

```
index = pd.TimeSeriesIndex()
columns = NGK_X, NGK_Y, NGK_Z, ..., ESK_X, ESK_Y, ESK_Z, ...
```

and Ap index from [GFZ](http://www.gfz-potsdam.de/en/kp-index/)

Finding steps. There is a list of baseline step corrections. We _think_ they have been applied before the data get to the stage that Grace's data is at. Not totally sure what has been done, maybe steps removed and then noted at the end of year.
There is currently an R-interface to find and remove step corrections but it would be better not to need to do this.

## what wanted
1. Per-observatory monthly means of `X, Y, Z` components. Discard all `I, F` only keep `H` to get `
2. Monthly 1st differences.
3. Initially, monthly means in folder structure like * above
4. List of observatories in _geocentric_ lat, lon, radius (prefereably in radians).

## Actions
- **Will** will find out how and when the baseline correction is done
- **Will** What spheroid are the lat lon etc. on INTERMAGNET and WDC websites with repect to. Prob geographic (WGS 84) and height MSL?
- **Will** Fork (or otherwise) [Grace's GitHub repo](https://github.com/gracecox/MagPy), make a `virtualenv` and run notebook. Wiht help from Grace and Laurence.
- **Will** answer some of the questions raised in the manuscript
- **Laurence** can we get location from WDC REST API (poss via [postman](http://www.getpostman.com/))?
- **Laurence** monthly mean data from WDC via REST API into folder structure in * above. Not _yet_ implimenting heirachy of defin, qdefin,
- **Grace** nudge Richard re letter of support for EPCC refactor
- **Grace** continue drafting paper

### time frame for actions

Laurence will have tiem to work on this
 between 2017-01-27/02-01




