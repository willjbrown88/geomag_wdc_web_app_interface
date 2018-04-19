"""
functional tests for getting geomag data via
requests to WDC and INTERMAGNET web services
"""
from datetime import date
import filecmp
import glob
import os
import zipfile

import pytest
import requests as rq
from six import BytesIO

from gmdata_webinterface import consume_webservices as cws

DATAPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'test_data'
)
ORACLEPATH = os.path.join(DATAPATH, 'known_good')


def assert_all_lines_same(path_1, path_2):
    """
    Compare files given by `path_1`, `path_2`
    line-by-line.
    Ignoring line-ending differences.
    (because of the way `open` works)
    Raises
    ------
    AssertionError if the files differ
    """
    line1 = line2 = ' '
    linenum = 0
    with open(path_1, 'r') as file1, open(path_2, 'r') as file2:
        while line1 != '' and line2 != '':
            line1 = file1.readline()
            line2 = file2.readline()
            if line1 != line2:
                mess = """files {} and {} differ on line {}
                "{}" !=
                "{}"
                """.format(path_1, path_2, linenum, line1, line2)
                raise AssertionError(mess)
            linenum += 1
    return None


def test_getting_wdc_format_hour_data_from_wdc(tmpdir):  # pylint: disable=invalid-name
    """
    smoke test WRT 'known good' data
    - download hourly averages of Niemegk from WDC
    - in wdc format
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

    config = cws.ParsedConfigFile(configpath, service)
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
    # custom function due to line-ending vagueries
    assert_all_lines_same(gotfile, oraclefile)


def test_getting_iaga_format_minute_data_from_wdc(tmpdir):  # pylint: disable=invalid-name
    """
    smoke test WRT 'known good' data
    - download a bunch of Eskdalemuir minutely averages
    - in IAGA2002 format
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
    # truth file names and full paths
    oraclenames, oraclefiles = zip(*[
            (os.path.basename(file_), file_) for file_ in
            glob.glob(os.path.join(ORACLEPATH, file_pattern))
            ])

    config = cws.ParsedConfigFile(configpath, service)
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

    # check lists of file names are same only (content comparison broken
    # by line endings)
    _, _, errs = filecmp.cmpfiles(tmppath, ORACLEPATH,
                                  oraclenames, shallow=False)
    assert errs == [], (
        "could not compare {} to expected, ".format(errs) +
        "perhaps we didn't download them"
    )

    # full paths to dowloaded files
    gotfiles = [os.path.join(tmppath, file_) for file_ in oraclenames]
    # custom file content comparison function due to line-ending vagueries
    [assert_all_lines_same(file1_, file2_) for file1_, file2_ in
        zip(gotfiles, oraclefiles)]


def test_fetch_station_data_wdc_format_hour_data_from_wdc(tmpdir):  # pylint: disable=invalid-name
    """
    make sure that our `fetch_station_data` wrapper function does the same as
    instantiating the classes, making the request,
    and saving the unpacked zip files sequentually
    """
    cadence = 'hour'
    station = 'NGK'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)
    service = 'WDC'
    expected_filename = 'ngk2015.wdc'
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_wdcoutput.ini')
    # TODO: cf fetch_station_data vs oracle files
    # oraclefile = os.path.join(ORACLEPATH, 'ngk2015.wdc')

    # ensure we have somewhere to put the data
    manualdir = os.path.join(str(tmpdir), 'manual')
    funcdir = os.path.join(os.path.dirname(manualdir),
                           'via__fetch_station_data')
    for dir_ in (manualdir, funcdir):
        os.mkdir(dir_)
    manualfile = os.path.join(manualdir, expected_filename)
    funcfile = os.path.join(funcdir, expected_filename)

    # 'manual' way
    config = cws.ParsedConfigFile(configpath, service)
    form_data = cws.FormData(config)
    form_data.set_datasets(start_date, end_date, station, cadence, service)
    req_wdc = cws.DataRequest()
    req_wdc.read_attributes(config)
    req_wdc.set_form_data(form_data.as_dict())
    resp_wdc = rq.post(
        req_wdc.url, data=req_wdc.form_data, headers=req_wdc.headers
    )

    cws.check_response(resp_wdc.status_code, resp_wdc.content)

    with zipfile.ZipFile(BytesIO(resp_wdc.content)) as fzip:
        fzip.extractall(manualdir)

    assert not os.path.isfile(funcfile)
    # with wrapper function
    cws.fetch_station_data(
        start_date=start_date, end_date=end_date,
        station=station, cadence=cadence,
        service=service, saveroot=funcdir, configpath=configpath
    )
    assert os.path.isfile(funcfile)
    assert_all_lines_same(funcfile, manualfile)


def test_fetch_data_wdc_format_hour_data_from_wdc(tmpdir):  # pylint: disable=invalid-name
    """
    make sure that our `fetch_data` wrapper function does the same as
    instantiating the classes, making the request,
    and saving the unpacked zip files sequentually
    """
    cadence = 'hour'
    stations = ['NGK', 'LER']
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)
    service = 'WDC'
    expected_filenames = ['ngk2015.wdc', 'ler2015.wdc']
    configpath = os.path.join(DATAPATH, 'wdc_minute_data_wdcoutput.ini')
    # TODO: cf fetch_data vs oracle files
    # oraclefile = os.path.join(ORACLEPATH, 'ngk2015.wdc')

    # ensure we have somewhere to put the data
    manualdir = os.path.join(str(tmpdir), 'manual')
    funcdir = os.path.join(os.path.dirname(manualdir), 'via__fetch_data')
    for dir_ in (manualdir, funcdir):
        os.mkdir(dir_)
    manualfile = []
    funcfile = []
    for filename_ in expected_filenames:
        manualfile.append(os.path.join(manualdir, filename_))
        funcfile.append(os.path.join(funcdir, filename_))

    # 'manual' way
    for station_ in stations:
        config = cws.ParsedConfigFile(configpath, service)
        form_data = cws.FormData(config)
        form_data.set_datasets(start_date, end_date, station_, cadence,
                               service)
        req_wdc = cws.DataRequest()
        req_wdc.read_attributes(config)
        req_wdc.set_form_data(form_data.as_dict())
        resp_wdc = rq.post(
            req_wdc.url, data=req_wdc.form_data, headers=req_wdc.headers
        )

        cws.check_response(resp_wdc.status_code, resp_wdc.content)

        with zipfile.ZipFile(BytesIO(resp_wdc.content)) as fzip:
            fzip.extractall(manualdir)

    for filepath_ in funcfile:
        assert not os.path.isfile(filepath_)
    # with wrapper function
    cws.fetch_data(
        start_date=start_date, end_date=end_date,
        station_list=stations, cadence=cadence,
        service=service, saveroot=funcdir, configpath=configpath
    )
    for filepath_ in funcfile:
        assert os.path.isfile(filepath_)
    [assert_all_lines_same(file1_, file2_) for file1_, file2_ in
        zip(funcfile, manualfile)]
