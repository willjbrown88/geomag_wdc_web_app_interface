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

def _check_service(config, service='WDC'):
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


def headers(config, service='WDC'):
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


def url_for_post(config, service='WDC'):
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
HEADERS = headers(config, service='WDC')
URL = url_for_post(config, service='WDC')

dSets = csDtBasename + station.lower() + str(year) + str(month).zfill(2)
if isinstance(dSets, str):
    dSets = [dSets]
cslDSets = ','.join(dSet for dSet in list(dSets))

payload_data[kyData] = cslDSets

payload_data[kyFmt] = fmtIaga
reqiaga = rq.post(URL, data=payload_data, headers=HEADERS)
with open('./esk_test_iaga2k2_{}.zip'.format(cadence), 'wb') as file_:
    file_.write(reqiaga.content)


payload_data[kyFmt] = fmtWdc
reqwdc = rq.post(URL, data=payload_data, headers=HEADERS)
with open('./esk_test_wdc_{}.zip'.format(cadence), 'wb') as file_:
    file_.write(reqwdc.content)
