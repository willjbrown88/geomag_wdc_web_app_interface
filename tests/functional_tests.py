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

import pytest
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
    service = 'WDC'
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_wdcoutput.ini')
    oraclefile = os.path.join(ORACLEPATH, 'ngk2015.wdc')

    tmppath = str(tmpdir)

    config = cws.RequestConfigParser(configpath, service)
    form_data = cws.FormData(config)
    with pytest.raises(ValueError):
        form_data.as_dict()
    form_data.set_datasets(start_date, end_date, station, cadence, service)
    req_wdc = cws.DataRequest()
    req_wdc.read_attributes(config)
    assert req_wdc.can_send is False
    assert req_wdc.form_data == {}
    req_wdc.set_form_data(form_data.as_dict())
    assert req_wdc.can_send is True

    resp_wdc = rq.post(
        req_wdc.url, data=req_wdc.form_data, headers=req_wdc.headers
    )

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
    service = 'WDC'
    year = 2015
    start_date = date(year, 1, 15)
    end_date = date(year, 12, 1)
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_iaga2002output.ini')
    file_pattern = station.lower() + str(year) + '*dmin.min'

    tmppath = str(tmpdir)  # pytest 'magic' for a temp folder
    oraclefiles = [os.path.basename(file_) for file_ in glob.glob(
        os.path.join(ORACLEPATH, file_pattern))]

    config = cws.RequestConfigParser(configpath, service)
    form_data = cws.FormData(config)
    with pytest.raises(ValueError):
        form_data.as_dict()
    form_data.set_datasets(start_date, end_date, station, cadence, service)
    req_iaga = cws.DataRequest()
    req_iaga.read_attributes(config)
    assert req_iaga.can_send is False
    assert req_iaga.form_data == {}
    req_iaga.set_form_data(form_data.as_dict())
    assert req_iaga.can_send is True

    resp_iaga = rq.post(
        req_iaga.url, data=req_iaga.form_data, headers=req_iaga.headers
    )
    with zipfile.ZipFile(BytesIO(resp_iaga.content)) as fzip:
        fzip.extractall(tmppath)
    sames, diffs, errs = filecmp.cmpfiles(tmppath, ORACLEPATH,
                                          oraclefiles, shallow=False)
    assert diffs == [], (
        'files {} downloaded '.format(diffs) +
        'but contents differ from known-good'
    )
    assert errs == [], (
        "could not compare {} to expected, ".format(errs) +
        "perhaps we didn't download them"
    )
    assert sames == oraclefiles, (
        'not all downloaded files are the same as known good ones'
    )
