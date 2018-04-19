"""
consume_webservices module

Consume the BGS-WDC (and, in future, INTERMAGNET) webservices.

main public function to call is `fetch_data(...)`.
Other functions and classes are for modularity/testability

Lots of the server interaction is controlled
by the `.ini` configuration file, as is
the download file structure.

@author: L Billingham; W. Brown
"""
import os
import zipfile
from datetime import timedelta
from configparser import ConfigParser, NoOptionError
import requests as rq
from six import BytesIO
from gmdata_webinterface.sandboxed_format import safe_format


def fetch_data(*, start_date, end_date, station_list, cadence, service,
               saveroot, configpath=None):
    """
    Wrapper for the wrapper `fetch_station_data()`...
    `fetch_station_data()` handles a single observatory, for a range of
    dates. Here, simply accept a list of `station` codes, and pass each value
    to `fetch_station_data()` with the remaining criteria kept constant.

    Parameters
    ----------
    start_date:  datetime.date
        earliest date at which data wanted.
    end_date:  datetime.datetime
        latest date at which data wanted.
    station: string, list of string
        IAGA-style station code e.g. 'ESK', 'NGK' or a list of such e.g.
        ['ESK, 'NGK']
    cadence: string
        frequency of the data. 'minute' or 'hour',
        changes the total data span
    service: string
        webservice to target, only  'WDC' for now
        (future work will support 'INTERMAGNET')
    saveroot: file path as string
        root directory at which to save data.
        multi-file downloads structured according to
        contents of `configpath`
    configpath: file path as string
        location of the configuration file we want to read, by default
        this will be the version included in the package install

    Returns
    -------
    None

    Notes
    -----
    Downloads data to the specified path.

    Raises
    ------
    ValueError if `cadence` is not something we can use
        (currently only 'minute' or 'hour')

    ConfigError if any of the required header values
        are not options within the config file

    InvalidRequest if we cannot make a sane request to `service` based
        on data provided via function arguments or the `configpath`

    InvalidResponse if the response is not the desired HTTP status code
    """

    if isinstance(station_list, str):
        station_list = station_list.split()

    [
        fetch_station_data(start_date=start_date, end_date=end_date,
                           station=station_, cadence=cadence, service=service,
                           saveroot=saveroot, configpath=configpath)
        for station_ in station_list
    ]


def fetch_station_data(*, start_date, end_date, station, cadence, service,
                       saveroot, configpath=None):
    """
    Ask webservice `service` for observatory data
    and download it to folder `saveroot`.
    The data to be requested are defined by `start_date`, `end_date`,
    `station`, and `cadence`.
    Aspects of the request and download folder structure are read
    from the configuration file at `configpath`

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
        webservice to target, only  'WDC' for now
        (future work will support 'INTERMAGNET')
    saveroot: file path as string
        root directory at which to save data.
        multi-file downloads structured according to
        contents of `configpath`
    configpath: file path as string
        location of the configuration file we want to read, by default
        this will be the version included in the package install

    Returns
    -------
    None

    Notes
    -----
    Downloads data to the specified path.

    Raises
    ------
    ValueError if `cadence` is not something we can use
        (currently only 'minute' or 'hour')

    ConfigError if any of the required header values
        are not options within the config file

    InvalidRequest if we cannot make a sane request to `service` based
        on data provided via function arguments or the `configpath`

    InvalidResponse if the response is not the desired HTTP status code
    """

    if configpath is None:
        configpath = os.path.join(os.path.dirname(__file__),
                                  'consume_rest.ini')

    config = ParsedConfigFile(configpath, service)
    form_data = FormData(config)
    form_data.set_datasets(start_date, end_date, station, cadence, service)
    request = DataRequest()
    request.read_attributes(config)
    request.set_form_data(form_data.as_dict())
    response = rq.post(
        request.url, data=request.form_data, headers=request.headers
    )
    check_response(response.status_code, response.content)

    # TODO: make this work with > 1 file without wrapper function
    with zipfile.ZipFile(BytesIO(response.content)) as fzip:
        fzip.extractall(saveroot)


def check_response(status_code, content):
    """
    Check if the server response is 'ok' (see `requests.codes`).
    It's probably 'ok' 200, or 'internal_server_error' 500 because the server
    is misbehaving.

    Parameters
    ----------
    status_code: http status code from post request response

    content: stream content from post request response

    Returns
    -------
    none

    Raises
    ------
    ValueError: if http code is not 'ok' (200), or is 'ok' but empty
        `filelist` returned

    """
    if status_code != rq.codes.ok:
        mess = ("unexpected http response code from server: " +
                "{}, '{}'")
        mess = mess.format(status_code,
                           rq.status_codes._codes[status_code][0])
        raise ValueError(mess)

    elif status_code == rq.codes.ok:
        """An empty zipfile will still send back some bytes but can check if
        the returned filelist is empty.
        """
        content = zipfile.ZipFile(BytesIO(content))
        if not content.filelist:
            mess = ("no valid files returned.\n" +
                    "http response code is: {}, '{}'\n" +
                    "data may not be available for date range " +
                    "requested, or server is misbehaving.")
            mess = mess.format(status_code,
                               rq.status_codes._codes[status_code][0])
            raise ValueError(mess)


class ConfigError(Exception):
    """Errors reading config files for consuming webservices"""
    pass


class InvalidRequest(ValueError):
    """
    The request is invalid: probably the parts are
    not fully populated
    """
    pass


class DataRequest(object):
    """
    The HTTP POST request for getting
    the geomag data we want

    Can set attributes by either
        * passing parameters at instantiation

    or
        * instantiating a 'blank' object and use the `my_req.set_*(config)`
        methods to populate all the required parts from a parse config file

    Attributes
    ----------
    can_send: bool
        Do we contain enough data that we can send a sensible request?
        N.B. does not do fancy validation.
    form_data: dict
        Dictionary of POST request form data
        e.g. {'format': 'text/x-wdc',
        'datasets': '/wdc/datasets/minute/aaa200509'}
    headers: dict
        Dictionary of request headers
        e.g. {'Accept': 'text/html,application/xml',
        'Content-Type': 'application/x-www-form-urlencoded'}
    url: string
        Full url to which we will make the request
        e.g. http://app.geomag.bgs.ac.uk/wdc/datasets/download

    """
    def __init__(self, url='', headers=None, form_data=None):
        """
        Attributes
        ----------
        url: string, default '',
            Full url to which we will make the request
            e.g. http://app.geomag.bgs.ac.uk/wdc/datasets/download
        headers: dict or (default) `None`
            Dictionary of request headers
            e.g. {'Accept': 'text/html,application/xml',
            'Content-Type': 'application/x-www-form-urlencoded'}
        form_data: dict or (default) `None`
            Dictionary of POST request form data
            e.g. {'format': 'text/x-wdc',
            'datasets': '/wdc/datasets/minute/aaa200509'}

        """
        self.url = url
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        if form_data is None:
            self.form_data = {}
        else:
            self.form_data = form_data

    @property
    def can_send(self):
        """
        have we populated enough data that we can send a request?
        """
        return bool(self.headers and self.form_data and self.url)

    def send(self):
        """
        Send a populated DataRequest

        Notes
        -----
        Makes an HTTP request over the network

        Raises
        ------
        InvalidRequest if we've not been fully populated
        """
        if not self.can_send:
            self._error_with_message()
        else:
            response = rq.post(url=self.url,
                               data=self.form_data, headers=self.headers)
            response.raise_for_status()
            return response

    def _error_with_message(self):
        """raise an error after building relevent error message"""
        mess_base = ('Cannot send request: missing {}; '
                     'set by calling `{}` method')
        mess = ''
        if not self.headers:
            mess += mess_base.format('headers', 'read_headers(config)')
        if not self.url:
            mess += mess_base.format('url', 'read_url(config)')
        if not self.form_data:
            mess += mess_base.format('form data',
                                     'set_form_data(form_data_dict)')
        raise InvalidRequest(mess)

    def read_url(self, request_config):
        """
        Get the request url from the config file using
        the ParsedConfigFile `config`

        Parameters
        ----------
        request_config: ParsedConfigFile
            thing that knows how to read `urls` from
            configuration files
        """
        self.url = request_config.url

    def read_headers(self, request_config):
        """
        Get the request headers from the config file using
        the ParsedConfigFile `config`

        Parameters
        ----------
        request_config: ParsedConfigFile
            thing that knows how to read from
            configuration files
        """
        self.headers = request_config.headers

    def read_attributes(self, request_config):
        """
        Get as many attributes as posible from the config file using
        the ParsedConfigFile `config`

        Parameters
        ----------
        request_config: ParsedConfigFile
            thing that knows how to read from
            configuration files
        """
        self.read_url(request_config)
        self.read_headers(request_config)

    def set_form_data(self, form_data_dict):
        """
        set our form_data attribute based on the
        passed dictionary of data

        Parameters
        ----------
        form_data_dict: dict
            something like
            {'datasets': '/route_url/aaa1978',
            'format':text/x-wdc}
        """
        self.form_data = form_data_dict


class FormData(object):
    """
    Holds sort of data we need to make a POST request via a form.
    Partially populates itself with data read from configuration file
    """
    def __init__(self, request_config):
        """
        Parameters
        ----------
        request_config: ParsedConfigFile
            thing that knows how to read  the expected return data
            format from configuration files
        """
        self.format = request_config.dataformat
        self.datasets = None
        self._from_req_parser = request_config

    def __str__(self):
        """pretty (ish) printing)"""
        strout = safe_format('{}:\n    {}', self.__class__.__name__,
                             self._dict)
        return strout

    def __repr__(self):
        args_part = safe_format('({})', self._from_req_parser)
        return self.__class__.__name__ + args_part

    def __eq__(self, other):
        same_format = self.format == other.format
        same_datasets = self.datasets == other.datasets
        return same_datasets and same_format

    def __ne__(self, other):
        return not self == other

    @property
    def _dict(self):
        """don't rely on this dict representation from outside"""
        return {'format': self.format, 'datasets': self.datasets}

    def as_dict(self):
        """
        Return a dictionary of data held by FormData.

        Raises
        ------
        ValueError:
            if we do not have valid data because we still need to
            work out e.g. the list of datasets for the form
        """
        if self.datasets is not None:
            return self._dict
        else:
            raise ValueError('datasets not valid, use '
                             '`set_datasets` method to populate')

    def set_datasets(self, start_date, end_date, station, cadence, service):
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
            webservice to target, only 'WDC' for now
            (+ 'INTERMAGNET' in future)

        Returns
        -------
        datasets for the POST request form in a a comma-seperated
            string.

        Raises
        ------
        ValueError if `cadence` is not either 'minute' or 'hour'
        """
        root = '/'.join(['', service.lower(), 'datasets', cadence, ''])
        cadences_supported = ['minute', 'hour']
        if cadence == 'hour':
            base = root + station.lower() + '{:d}'
            years = range(start_date.year, end_date.year + 1)
            dsets = (safe_format(base, year) for year in years)
        elif cadence == 'minute':
            base = root + station.lower() + '{:d}{:02d}'
            # note the creation of per-diem date stamps followed by a
            #   set comprehension over their strings appears wasteful because
            #   it creates ~30X more date objects than we strictly need.
            #   but doing the maths correctly ourselves
            #   including edge and corner cases is
            #   messy, complex, and easy to screw up

            # +1 so we _include_ the end date in range
            num_days = (end_date - start_date).days + 1
            all_days = (start_date + timedelta(day) for day in range(num_days))
            dsets = {safe_format(base, dt.year, dt.month) for dt in all_days}
        else:
            mess = 'cadence {} cannot be handled.\nShould be one of: {}'
            raise ValueError(safe_format(mess, cadence, cadences_supported))
        self.datasets = ','.join(dset for dset in dsets)


class ParsedConfigFile(object):
    """
    Read the configuration file for making requests to
    the WDC  (and, in future INTERMAGNET) webservices.

    Notes
    -----
    File is read on instantiation, but methods to
    extract parts needed are public `extract_url` etc.

    Parameters
    ----------
    config_file: file path (string)
        location of the configuration file we want to read
    target_service: string
        Which we service are we targeting?
        Currently only 'WDC'.

    Attributes
    ----------
    dataformat: string
        format we want observatory data to come back in.
        Becomes part of the FormData.
        Typically contains filetype e.g. 'text/x-iaga2002'
    service: string
        the geomag webservice to which to make the request,
        e.g. 'WDC' or (in future) 'INTERMAGNET'
    headers: `dict` of strings
        header values for the HTTP the request,
        e.g. {'Accept-Encoding': 'gzip'}
    url: string
        The URL to which we will send the request

    Raises
    ------
    ConfigError if any of the required header values
    are not options within the config file
    """
    headers_need = ['Accept', 'Accept-Encoding', 'Content-Type']
    urlbits_need = ['Hostname', 'Route']

    def __init__(self, config_file, target_service):
        """ see class docstring """
        self._filename = config_file
        self._config = ConfigParser()
        self._config.read(self._filename)
        self._check_service(target_service)
        self.service = target_service
        self.headers = self.extract_headers()
        self.url = self.extract_url()
        self.dataformat = self.form_data__format()

    def __repr__(self):
        mess = safe_format(
            '{}({}, {})',
            self.__class__.__name__,
            repr(self._filename),
            repr(self.service)
        )
        return mess

    def extract_headers(self):
        """
        Get the request headers from the ConfigurationParser `config`.
        `service` is assumed to be a section in the `config`

        Returns
        -------
        `dict` of headers for the request

        Raises
        ------
        ConfigError if any of the required header values
        are not options within the config file
        """
        try:
            heads = {
                k: self._config.get(self.service, k) for k in self.headers_need
            }
        except NoOptionError as err:
            mess = (
                'cannot load request headers from config\n' +
                'require values for {0}\n' +
                'under section for service `[{1}]`\n' +
                'found only {2}\n' +
                str(err)
            )
            formatted_mess = safe_format(
                mess,
                self.headers_need,
                self.service,
                list(self._config[self.service].keys())
            )
            raise ConfigError(formatted_mess)
        return heads

    def extract_url(self):
        """
        Form the URL to send the request to
        by reading the ConfigurationParser `config`

        Returns
        -------
        url for request as a `str`

        Raises
        ------
        ConfigError if any of the required parts of the url are not options
        within the config file
        """
        try:
            url = '/'.join(
                self._config.get(self.service, k) for k in self.urlbits_need
            )
        except NoOptionError as err:
            mess = (
                'cannot load request url from config\n' +
                'require values for {0}\n' +
                'under section for service `[{1}]`\n' +
                'found only {2}\n' +
                str(err)
            )
            formatted = safe_format(
                mess,
                self.urlbits_need,
                self.service,
                list(self._config[self.service].keys())
                )
            raise ConfigError(formatted)
        return url

    def form_data__format(self):
        """
        The format for the output files as read from the config.

        N.B.
        The double_underscore (`__`) in the name is trying to indicate
        that we are reading the 'format' part of the 'form_data'
        from the config file.... inspired by
        [django's usage](http://stackoverflow.com/questions/5481682)

        Returns
        -------
        dataformat: string:
            What format do we want the response data to be in
            when we make a request?

        Raises
        ------
        ConfigError if cannot make valid data format selection
        from options within the config file
        """
        template_option = '_format_template'
        outfile_option = 'FileFormat'
        try:
            outfmt_template = self._config.get(self.service, template_option)
        except NoOptionError:
            mess = (
                'cannot find required value {}\n' +
                'in config for service:{}'
            )
            formatted_mess = safe_format(mess, template_option, self.service)
            raise ConfigError(formatted_mess)
        try:
            outfiletype = self._config.get(self.service, outfile_option)
        except NoOptionError:
            mess = (
                'cannot find "FileType" option value {}\n' +
                'in config for service:{}'
            )
            formatted_mess = safe_format(mess, outfile_option, self.service)
            raise ConfigError(formatted_mess)
        final_format = safe_format(outfmt_template, outfiletype)
        return final_format

    def _check_service(self, service):
        """
        Validate the `service` by ensuring the config file has a section
        of options for the `service` we are interested in.

        Parameters
        ----------
        service: string
            webservice to target, either 'WDC' (or,
            in future 'INTERMAGNET')
        """
        if service not in self._config.sections():
            mess = (
                'cannot find service:{0} in configuration\n' +
                'should look like (like `[{0}]`)\n' +
                'found sections for {1}\n'
            )
            formatted_mess = safe_format(
                mess, service, self._config.sections()
            )
            raise ConfigError(formatted_mess)


if __name__ == '__main__':
    pass  # this is module is only for being imported
