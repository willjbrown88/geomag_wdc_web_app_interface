"""
functional tests for getting geomag data via
requests to WDC and INTERMAGNET web services
"""
from configparser import ConfigParser
from datetime import date
import filecmp
import glob
import os
import zipfile

import requests as rq
from six import BytesIO

from lib import consume_webservices as cws

DATAPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'test_data'
)
ORACLEPATH = os.path.join(DATAPATH, 'known_good')

def test_getting_wdc_format_hour_data_from_wdc(tmpdir):
    """
    smoke test WRT 'known good' data
    - downlad hourly averages of Niemeg from WDC
    - put them in a temporary folder
    - compare them with 'known-good' examples
    """
    cadence = 'hour'
    station = 'NGK'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_wdcoutput.ini')
    oraclefile = os.path.join(ORACLEPATH, 'ngk2015.wdc')

    tmppath = str(tmpdir)

    config = ConfigParser()
    config.read(configpath)
    headers = cws.extract_headers(config, service='WDC')
    url = cws.extract_url(config, service='WDC')
    payload_data = cws.form_data(start_date, end_date, station,
                                 cadence, config, 'WDC')

    resp_wdc = rq.post(url, data=payload_data, headers=headers)
    with zipfile.ZipFile(BytesIO(resp_wdc.content)) as fzip:
        fzip.extractall(tmppath)
    gotfile = os.path.join(tmppath, os.path.basename(oraclefile))
    assert filecmp.cmp(gotfile, oraclefile, shallow=False), (
        "response differs from 'known-good' file"
    )


def test_getting_iaga_format_minute_data_from_wdc(tmpdir):
    """
    smoke test WRT 'known good' data
    - download a bunch of Eskdalemuir minutely averages
    - extract them to a temp dir
    - compare each downloaded files against known-good examples
    """
    cadence = 'minute'
    station = 'ESK'
    year = 2015
    start_date = date(year, 1, 15)
    end_date = date(year, 12, 1)
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_iaga2002output.ini')
    file_pattern = station.lower() + str(year) + '*dmin.min'

    tmppath = str(tmpdir)  # pytest 'magic' for a temp folder
    oraclefiles = [os.path.basename(file_) for file_ in glob.glob(
        os.path.join(ORACLEPATH, file_pattern))]

    config = ConfigParser()
    config.read(configpath)
    headers = cws.extract_headers(config, service='WDC')
    url = cws.extract_url(config, service='WDC')
    payload_data = cws.form_data(start_date, end_date, station, cadence,
                                 config, 'WDC')

    resp_iaga = rq.post(url, data=payload_data, headers=headers)
    with zipfile.ZipFile(BytesIO(resp_iaga.content)) as fzip:
        fzip.extractall(tmppath)
    sames, diffs, errs = filecmp.cmpfiles(tmppath, ORACLEPATH,
                                          oraclefiles, shallow=False)
    assert diffs == [], (
        'files {} downloaded but contents differ from known-good '.format(diffs)
    )
    assert errs == [], (
        "could not compare {} to expected, ".format(errs) +
        "perhaps we didn't download them"
    )
    assert sames == oraclefiles, (
        'not all downloaded files are the same as known good ones'
    )