"""
functional tests for getting geomag data via
requests to WDC and INTERMAGNET web services
"""
from configparser import ConfigParser
from datetime import date
import os

import requests as rq

from lib import consume_webservices as cws

DATAPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'test_data'
)


def test_getting_iaga_format_minute_data_from_wdc():
    """
    smoke test WRT 'known good' data
    of minutely averages
    """
    cadence = 'minute'
    station = 'ESK'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_iaga2002output.ini')

    config = ConfigParser()
    config.read(configpath)
    headers = cws.extract_headers(config, service='WDC')
    url = cws.extract_url(config, service='WDC')

    payload_data = cws.form_data(start_date, end_date, station, cadence,
        config, 'WDC')

    resp_wdc = rq.post(url, data=payload_data, headers=headers)
    with open('./{}_test_wdc_{}.zip'.format(station, cadence), 'wb') as file_:
        file_.write(resp_wdc.content)
    assert False  # finish the test by comparing to known-good


def test_getting_wdc_format_hour_data_from_wdc():
    """
    smoke test WRT 'known good' data
    of minutely averages
    """
    cadence = 'hour'
    station = 'NGK'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_wdcoutput.ini')

    config = ConfigParser()
    config.read(configpath)
    headers = cws.extract_headers(config, service='WDC')
    url = cws.extract_url(config, service='WDC')

    payload_data = cws.form_data(start_date, end_date, station,
        cadence, config, 'WDC')
    resp_iaga = rq.post(url, data=payload_data, headers=headers)
    with open('./{}_test_iaga2k2_{}.zip'.format(station, cadence), 'wb') as file_:
        file_.write(resp_iaga.content)
    assert False  # finish the test by comparing to known-good