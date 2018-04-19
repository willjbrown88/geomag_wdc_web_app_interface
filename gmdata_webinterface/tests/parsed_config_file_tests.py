"""
tests for the reading of config files for
bits of websrevice requests that will not change much
"""
import configparser

import pytest

from gmdata_webinterface.consume_webservices import ParsedConfigFile, ConfigError

# these small Mock classes are OK weird
# pylint: disable=missing-docstring, no-self-use
THE_SERVICE = 'ABC'


class MockCfgParser(object):
    """
    fake just enough of the bits from
    std lib's configparser.ConfigParser
    that we can drop this in for testing
    and not have to read a real config file
    """
    header_bits = {
        'Accept': 'spam',
        'Accept-Encoding': 'ham',
        'Content-Type': 'eggs',
    }
    url_bits = {
        'Hostname': 'foo',
        'Route': 'bar',
    }
    for_form_bits = {
        'FileFormat': 'beep',
        '_format_template': '{}-boop'
    }

    def __init__(self):
        self.data = {**self.header_bits,
                     **self.url_bits,
                     **self.for_form_bits}

    def __getitem__(self, _):
        return self.data

    def read(self, _):
        return None

    def sections(self):
        return [THE_SERVICE]

    def get(self, _, key):
        try:
            return self.data[key]
        except KeyError:
            raise configparser.NoOptionError(key, THE_SERVICE)

# pylint: enable=missing-docstring, no-self-use


def test_construction(monkeypatch):
    """can we make a new instance of a ParsedConfigFile?"""
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', MockCfgParser)
    got = ParsedConfigFile('afile', THE_SERVICE)
    assert got.service == THE_SERVICE
    # test failure to find service raises sane error
    not_in_there_service = 'Wally the service'
    with pytest.raises(ConfigError) as err:
        got = ParsedConfigFile('somefilepath', not_in_there_service)
    err_mess = str(err.value)
    for str_ in [not_in_there_service, THE_SERVICE]:
        assert str_ in err_mess


def test_repr(monkeypatch):
    """does `repr` and `eval` roundtrip to correct new instance?"""
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', MockCfgParser)
    filename = 'a-very-good.file'
    original = ParsedConfigFile(filename, THE_SERVICE)
    via_repr = eval(repr(original))   # pylint: disable=eval-used; OK for testing repr
    assert via_repr.service == original.service
    assert repr(via_repr) == repr(original)
    for instance in (original, via_repr):
        assert filename in repr(instance)


def test_extract_headers_happy_path(monkeypatch):
    """can we sucessfully extract headers from config file?"""
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', MockCfgParser)
    parser = ParsedConfigFile('whatever', THE_SERVICE)
    got_headers = parser.extract_headers()
    expected = MockCfgParser.header_bits
    for key, expected_value in expected.items():
        assert expected_value == got_headers[key]


def test_extract_headers_sad_path(monkeypatch):
    """
    if we can't extract headers from config file,
    do we fail with a sane error message?
    """
    # small weird Mocks OK
    # pylint: disable=missing-docstring
    class BadCfgParser(MockCfgParser):
        header_bits = {
            'NOTAccept': 'spam',
            'NOTAccept-Encoding': 'ham',
            'NOTContent-Type': 'eggs'
        }
    # pylint: enable=missing-docstring
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', BadCfgParser)
    with pytest.raises(ConfigError) as err:
        ParsedConfigFile('whatever', THE_SERVICE)
    err_mess = str(err.value)
    for str_ in ['section', "'NOTAccept'", "'Accept'", THE_SERVICE]:
        assert str_ in err_mess


def test_extract_url_happy_path(monkeypatch):
    """able to get URL from config file?"""
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', MockCfgParser)
    parser = ParsedConfigFile('whatever', THE_SERVICE)
    got_url = parser.extract_url()
    expected_bits = MockCfgParser().url_bits
    expected_url = '{}/{}'.format(expected_bits['Hostname'],
                                  expected_bits['Route'])
    assert expected_url in got_url


def test_extract_url_sad_path(monkeypatch):
    """
    do we raise an appropriate error
    if we cannot get the bits we need from the config?
    """
    class BadCfgParser(MockCfgParser):  # pylint: disable=missing-docstring
        url_bits = {
            'NOTHostname': 'foo',
            'NOTRoute': 'bar',
        }
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', BadCfgParser)
    with pytest.raises(ConfigError) as err:
        ParsedConfigFile('whatever', THE_SERVICE)
    err_mess = str(err.value)
    for str_ in ['section',
                 "'NOTRoute'", "'Route'",
                 "'NOTHostname'", "'Hostname'",
                 THE_SERVICE]:
        assert str_ in err_mess


def test_form_data__format_happy_path(monkeypatch):  # pylint: disable=invalid-name
    """
    can we read bits we expect out of a valid config file?
    """
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', MockCfgParser)
    parser = ParsedConfigFile('whatever', THE_SERVICE)
    got_fmt = parser.form_data__format()
    expected_fmt = 'beep-boop'
    assert got_fmt == expected_fmt


def test_form_data__format_sad_no_format_template(monkeypatch):  # pylint: disable=invalid-name
    """raise appropriate error if cannot get template from config?"""
    class BadCfgParser(MockCfgParser):  # pylint: disable=missing-docstring
        for_form_bits = {
            'FileFormat': 'beep',
            'no_format_template': 'here'
        }
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', BadCfgParser)
    with pytest.raises(ConfigError) as err:
        ParsedConfigFile('whatever', THE_SERVICE)
    err_mess = str(err.value)
    for str_ in ['service', THE_SERVICE, 'find']:
        assert str_ in err_mess


def test_form_data__format_sad_no_file_format(monkeypatch):  # pylint: disable=invalid-name
    """raise error if can't get file format from config?"""
    class BadCfgParser(MockCfgParser):  # pylint: disable=missing-docstring
        for_form_bits = {
            'NoFileFormatHere': 'beep',
            '_format_template': 'here'
        }
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', BadCfgParser)
    with pytest.raises(ConfigError) as err:
        ParsedConfigFile('whatever', THE_SERVICE)
    err_mess = str(err.value)
    for str_ in ['config', THE_SERVICE, 'find']:
        assert str_ in err_mess


def test_reads_supplied_filename(monkeypatch):
    """
    do we actually try to read the config file
    whose name we supply
    """
    class SpyCfgParser(MockCfgParser):
        """a config class that logs read method calls"""
        read_call_count = 0
        read_called_with = 'walrus'

        @classmethod
        def read(cls, arg):
            cls.read_call_count += 1
            cls.read_called_with = str(arg)

    monkeypatch.setattr('gmdata_webinterface.consume_webservices.ConfigParser', SpyCfgParser)

    filename = 'a_unique_file.name'
    assert SpyCfgParser.read_call_count == 0
    assert SpyCfgParser.read_called_with == 'walrus'
    ParsedConfigFile(filename, THE_SERVICE)
    assert SpyCfgParser.read_call_count == 1
    assert SpyCfgParser.read_called_with == filename
