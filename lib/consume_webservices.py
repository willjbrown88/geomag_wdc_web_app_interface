"""
Consume the BGS-WDC and INTERMAGNET webservices.
Lots of the server unteraction is controlled
by the `.ini` configuration file.
"""
from configparser import ConfigParser, NoOptionError, NoSectionError
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


def extract_output_file_format(config, service='WDC'):
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

    return {fmt_key: outfmt_template.format(outfiletype)}




def form_request_payload(station, year, month, config, service='WDC'):
    """form the POST request payload"""
    out_format = extract_output_file_format(config, service)
    raise NotImplementedError



kyFmt = 'format'
kyData = 'datasets'
cadence = 'minute'
csDtBasename = '/wdc/datasets/{}/'.format(cadence)
fmtIaga = 'text/x-iaga2002'
fmtWdc = 'text/x-wdc'
station = 'ESK'
year = 2015
month = 4

payload_data = {'format': '', 'datasets': ''}

config = ConfigParser()
config.read(CONFIGPATH)
HEADERS = extract_headers(config, service='WDC')
URL = extract_url(config, service='WDC')

dSets = csDtBasename + station.lower() + str(year) + str(month).zfill(2)
if isinstance(dSets, str):
    dSets = [dSets]
cslDSets = ','.join(dSet for dSet in list(dSets))

payload_data[kyData] = cslDSets


payload_data[kyFmt] = fmtIaga
fmt_map = extract_output_file_format(config, service='WDC')
payload_data = {**fmt_map, **{kyData: cslDSets}}

reqiaga = rq.post(URL, data=payload_data, headers=HEADERS)
with open('./{}_test_wdc_{}.zip'.format(station, cadence), 'wb') as file_:
    file_.write(reqiaga.content)


payload_data[kyFmt] = fmtIaga
reqwdc = rq.post(URL, data=payload_data, headers=HEADERS)
with open('./{}_test_iaga2k2_{}.zip'.format(station, cadence), 'wb') as file_:
    file_.write(reqwdc.content)
