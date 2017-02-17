"""
Consume the BGS-WDC and INTERMAGNET webservices.
Lots of the server unteraction is controlled
by the `.ini` configuration file.
"""
from configparser import ConfigParser, NoOptionError
from datetime import date, timedelta
from os import path as pth

import requests as rq


class ConfigError(Exception):
    """Errors reading config files for consuming webservices"""
    pass


class DataRequest(object):
    """
    The HTTP POST request for getting
    the geomag data we want

    Can set attributes by either:
    - passing parameters at instantiation
    or
    - instantiating a 'blank' object and use the `my_req.set_*(config)` methods
      to populate all the required parts from a parse config file

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
        have we populated enough data thatt we can send a request?
        """
        if self.headers and self.form_data and self.url:
            return True
        else:
            return False

    def read_url(self, request_config):
        """
        Get the request url from the config file using
        the RequestConfigParser `config`

        Parameters
        ---------
        request_config: RequestConfigParser
            thing that knows how to read `urls` from
            configuration files
        """
        self.url = request_config.extract_url()

    def read_headers(self, request_config):
        """
        Get the request headers from the config file using
        the RequestConfigParser `config`

        Parameters
        ---------
        request_config: RequestConfigParser
            thing that knows how to read from
            configuration files
        """
        self.headers = request_config.extract_headers()

    def read_attributes(self, request_config):
        """
        Get as many attributes as posible from the config file using
        the RequestConfigParser `config`

        Parameters
        ---------
        request_config: RequestConfigParser
            thing that knows how to read from
            configuration files
        """
        self.read_url(request_config)
        self.read_headers(request_config)

    def set_form_data(self, form_data_dict):
        self.form_data = form_data_dict


class FormData(object):
    """
    Holds sort of data we need to make a POST request via a form.
    Partially populates itself with data read from configuration file
    """
    def __init__(self, request_config):
        """
        Parameters
        ---------
        request_config: RequestConfigParser
            thing that knows how to read  the expected return data
            format from configuration files
        """
        self.format = request_config.form_data__format()
        self.datasets = None
        self._from_req_parser = request_config

    def __str__(self):
        """pretty (ish) printing)"""
        return '{}:\n    {}'.format(self.__class__.__name__, self._dict)

    def __repr__(self):
        args_part = '({})'.format(self._from_req_parser)
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
        cadences_supported = ['minute', 'hour']
        if cadence == 'hour':
            base = root + station.lower() + '{:d}'
            years = range(start_date.year, end_date.year + 1)
            dsets = (base.format(year) for year in years)
        elif cadence == 'minute':
            base = root + station.lower() + '{:d}{:02d}'
            # note the creation of per-diem date stamps followed by a
            #   set comprehension over their strings appears wasetful because
            #   it creates ~30X more date objects than we strictly need.
            #   but doing the maths correctly ourselves
            #   including edge and corner cases is
            #   messy, complex, and easy to screw up

            # +1 so we _include_ the end date in range
            num_days = (end_date - start_date).days + 1
            all_days = (start_date + timedelta(day) for day in range(num_days))
            dsets = {base.format(dt.year, dt.month) for dt in all_days}
        else:
            mess = 'cadence {} cannot be handled.\nShould be one of: {}'
            raise ValueError(mess.format(cadence, cadences_supported))
        self.datasets = ','.join(dset for dset in dsets)


class RequestConfigParser(object):
    """
    Knows how to read the configuration file for making requests to
    the WDC and INTERMAGNET webservices
    """
    def __init__(self, config_file, target_service):
        """
        Parameters
        ----------
        config_file: file path (string)
            location of the configuration file we want to read
        target_service: string
            Which we bervice are we targeting? Currently only
            'WDC'
        """
        self._from_file = config_file
        self.config = ConfigParser()
        self.config.read(config_file)
        self._check_service(target_service)
        self.service = target_service

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__, repr(self._from_file), repr(self.service)
        )

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
        head_keys = ['Accept', 'Accept-Encoding', 'Content-Type']

        try:
            heads = {k: self.config.get(self.service, k) for k in head_keys}
        except NoOptionError as err:
            mess = (
                'cannot load request headers from config\n' +
                'require values for {0}\n' +
                'under section for service `[{1}]`\n' +
                str(err)
            )
            raise ConfigError(mess.format(head_keys, self.service))
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
        url_keys = ['Hostname', 'Route']
        try:
            url = '/'.join(self.config.get(self.service, k) for k in url_keys)
        except NoOptionError as err:
            mess = (
                'cannot load request url from config\n' +
                'require values for {0}\n' +
                'under section for service `[{1}]`\n' +
                str(err)
            )
            raise ConfigError(mess.format(url_keys, self.service))
        return url

    def form_data__format(self):
        """
        The format for the output files as read from the config.

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
        fmt_key = 'format'
        try:
            outfmt_template = self.config.get(self.service, template_option)
        except NoOptionError:
            mess = (
                'cannot find required value {}\n' +
                'in config for service:{}'
            )
            raise ConfigError(mess.format(template_option, self.service))
        try:
            outfiletype = self.config.get(self.service, outfile_option)
        except NoOptionError:
            mess = (
                'cannot find FileType option value {}\n' +
                'in config for service:{}'
            )
            raise ConfigError(mess.format(outfile_option, self.service))
        return outfmt_template.format(outfiletype)

    def _check_service(self, service):
        """
        Validate the `service` by ensuring the config file has a section
        of options for the `service` we are interested in.

        Parameters
        ----------
        service: string
            webservice to target, either 'WDC' or
            'INTERMAGNET'
        """
        if service not in self.config.sections():
            mess = (
                'cannot find service:{0} in configuration\n' +
                'should look like (like `[{0}]`)\n' +
                'found sections for {1}\n'
            )
            raise ConfigError(mess.format(service, self.config.sections()))


def rubbish_funtional_test():
    configpath = pth.join(pth.dirname(pth.abspath(__file__)),
                          'consume_rest.ini')
    cadence = 'minute'
    station = 'ESK'
    service = 'WDC'
    start_date = date(2015, 4, 1)
    end_date = date(2015, 4, 30)

    config = RequestConfigParser(configpath, service)
    req = DataRequest()
    req.read_attributes(config)
    form_data = FormData(config)
    form_data.set_datasets(start_date, end_date, station, cadence, service)
    req.set_form_data(form_data.as_dict())

    resp = rq.post(req.url, data=req.form_data, headers=req.headers)
    with open('./{}_test_wdc_{}.zip'.format(station, cadence), 'wb') as file_:
        file_.write(resp.content)

    payload_data = req.form_data
    payload_data['format'] = 'text/x-iaga2002'
    resp_iaga = rq.post(req.url, data=payload_data, headers=req.headers)
    with open('./{}_test_iaga2k2_{}.zip'.format(station,
                                                cadence), 'wb') as file_:
        file_.write(resp_iaga.content)


if __name__ == '__main__':
    pass  # rubbish_funtional_test()
