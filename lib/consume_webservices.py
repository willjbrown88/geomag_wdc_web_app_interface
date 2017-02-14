"""
Consume the BGS-WDC and INTERMAGNET webservices.
Lots of the server unteraction is controlled
by the `.ini` configuration file.
"""
from configparser import ConfigParser, NoOptionError
from datetime import date, timedelta
from os import path as pth

import requests as rq

CONFIGPATH = pth.join(pth.dirname(pth.abspath(__file__)), 'consume_rest.ini')


class ConfigError(Exception):
    """Errors reading config files for consuming webservices"""
    pass


def _check_service(config, service):
    """
    ensure we have a section  about `service` in the
    configuration
    """
    if service not in config.sections():
        mess = (
            'cannot find service:{0} in configuration\n' +
            'should look like (like `[{0}]`)\n' +
            'found sections for {1}\n'
        )
        raise ConfigError(mess.format(service, config.sections()))


def extract_headers(config, service='WDC'):
    """
    Get the request headers from the ConfigurationParser `config`.
    `service` is assumed to be a section in the `config`

    Returns
    -------
    `dict` of headers for the request
    """
    head_keys = ['Accept', 'Accept-Encoding', 'Content-Type']

    _check_service(config, service)
    try:
        heads = {k: config.get(service, k) for k in head_keys}
    except NoOptionError as err:
        mess = (
            'cannot load request headers from config\n' +
            'require values for {0}\n' +
            'under section for service `[{1}]`\n' +
            str(err)
        )
        raise ConfigError(mess.format(head_keys, service))
    return heads


def extract_url(config, service='WDC'):
    """
    Form the URL to send the request to
    by reading the ConfigurationParser `config`

    Returns
    -------
    url for request as a `str`
    """
    url_keys = ['Hostname', 'Route']
    _check_service(config, service)
    try:
        url = '/'.join(config.get(service, k) for k in url_keys)
    except NoOptionError as err:
        mess = (
            'cannot load request url from config\n' +
            'require values for {0}\n' +
            'under section for service `[{1}]`\n' +
            str(err)
        )
        raise ConfigError(mess.format(url_keys, service))
    return url


def format_form_data(config, service='WDC', ret_dict=True):
    """
    The format for the output files as read fromthe config.
    """
    template_option = '_format_template'
    outfile_option = 'FileFormat'
    fmt_key = 'format'
    _check_service(config, service)
    try:
        outfmt_template = config.get(service, template_option)
    except NoOptionError:
        mess = (
            'cannot find required value {}\n' +
            'in config for service:{}'
        )
        raise ConfigError(mess.format(template_option, service))
    try:
        outfiletype = config.get(service, outfile_option)
    except NoOptionError:
        mess = (
            'cannot find FileTyp option value {}\n' +
            'in config for service:{}'
        )
        raise ConfigError(mess.format(outfile_option, service))
    if ret_dict:
        return {fmt_key: outfmt_template.format(outfiletype)}
    else:
        return outfmt_template.format(outfiletype)


def datasets_form_data(start_date, end_date, station, cadence, service='WDC'):
    """
    List of datasets for the POST request form data.

    The total span of data will be adjusted based on `cadence`
    so that both `start_date` and `end_date` are included.
    Total data span downloaded is likely to be
    longer than `end_date - start_date`

    Parameters
    ----------
    start_date:  datetime.date
        earliest date at which data wanted.
    end_date:  datetime.datetime
        latest date at which data wanted.
    station: string
        IAGA-style station code e.g. 'ESK', 'NGK'
    cadence: string
        frequency of the data. 'minute' or 'hour',
        changes the total data span
    service: string
        webservice to target, either 'WDC' or
        'INTERMAGNET'
    Returns
    -------
    datasets for the POST request form in a a comma-seperated
        string.

    Raises
    ------
    ValueError if `cadence` is not either 'minute' or 'hour'
    """
    root = '/'.join(['', service.lower(), 'datasets', cadence, ''])
    if cadence == 'hour':
        base = root + station.lower() + '{:d}'
        years = range(start_date.year, end_date.year + 1)
        dsets = (base.format(year) for year in years)
    elif cadence == 'minute':
        base = root + station.lower() + '{:d}{:02d}'
        # note the creation of per-diem date stamps followed by a
        # set comprehension over their strings appears wasetful because it
        # creates ~30X more date objects than we strictly need.
        #  but doing the maths correctly ourselves
        #  including edge and corner cases is
        #  messy, complex, and easy to screw up
        num_days = (end_date - start_date).days
        all_days = (start_date + timedelta(day) for day in range(num_days))
        dsets = {base.format(dt.year, dt.month) for dt in all_days}
    else:
        cadences_supported = ['minute', 'hour']
        mess = 'cadence {} cannot be handled.\nShould be one of: {}'
        raise ValueError(mess.format(cadence, cadences_supported))
    return ','.join(dset for dset in dsets)




def form_data(start_date, end_date, station, cadence, config, service='WDC'):
    """construct the POST request payload"""
    format_key = 'format'
    data_key = 'datasets'
    data_format = format_form_data(config, service, ret_dict=False)
    datasets = datasets_form_data(start_date, end_date, station, cadence, service='WDC')
    return {format_key: data_format, data_key: datasets}



def rubbish_funtional_test():
    cadence = 'minute'
    station = 'ESK'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)

    config = ConfigParser()
    config.read(CONFIGPATH)
    headers = extract_headers(config, service='WDC')
    url = extract_url(config, service='WDC')

    payload_data = form_data(start_date, end_date, station, cadence, config, 'WDC')

    resp_wdc = rq.post(url, data=payload_data, headers=headers)
    with open('./{}_test_wdc_{}.zip'.format(station, cadence), 'wb') as file_:
        file_.write(resp_wdc.content)


    payload_data['format'] = 'text/x-iaga2002'
    resp_iaga = rq.post(url, data=payload_data, headers=headers)
    with open('./{}_test_iaga2k2_{}.zip'.format(station, cadence), 'wb') as file_:
        file_.write(resp_iaga.content)


if __name__ == '__main__':
    rubbish_funtional_test()