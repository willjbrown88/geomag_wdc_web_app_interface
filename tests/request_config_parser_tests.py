import configparser
import pytest
from lib.consume_webservices import RequestConfigParser, ConfigError

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
        '_format_template': 'boop'
    }
    def __init__(self):
        self.data = {**self.header_bits,
                     **self.url_bits,
                     **self.for_form_bits}
    def __getitem__(self, _):
        return self.data
    def read(self, _):
        return None
    def sections(_):
        return [THE_SERVICE]
    def get(self, _, key):
        try:
            return self.data[key]
        except KeyError:
            raise configparser.NoOptionError(key, THE_SERVICE)


def test_construction(monkeypatch):
    """can we make a new instance of a RequestConfigParser?"""
    monkeypatch.setattr('lib.consume_webservices.ConfigParser', MockCfgParser)
    got = RequestConfigParser('afile', THE_SERVICE)
    assert got.service == THE_SERVICE
    # test failure raises sane error
    with pytest.raises(ConfigError) as err:
        got = RequestConfigParser('afile', 'Wally the service')
    err_mess = str(err.value)
    for str_ in ['Wally the service', THE_SERVICE]:
        assert str_ in err_mess


def test_repr(monkeypatch):
    """does `repr` and `eval` roundtrip to correct new instance?"""
    monkeypatch.setattr('lib.consume_webservices.ConfigParser', MockCfgParser)
    filename = 'a-very-good.file'
    original = RequestConfigParser(filename, THE_SERVICE)
    via_repr = eval(repr(original))
    assert via_repr.service == original.service
    assert via_repr.filename == original.filename == filename


def test_extract_headers_happy_path(monkeypatch):
    """can we sucessfully extract headers from config file?"""
    monkeypatch.setattr('lib.consume_webservices.ConfigParser', MockCfgParser)
    parser = RequestConfigParser('whatever', THE_SERVICE)
    got_headers = parser.extract_headers()
    expected = MockCfgParser.header_bits
    for key in expected.keys():
        assert expected[key] == got_headers[key]


def test_extract_headers_sad_path(monkeypatch):
    """
    if we can't extract headers from config file,
    do we fail with a sane error message?
    """
    class BadCfgParser(MockCfgParser):
        header_bits = {
            'NOTAccept': 'spam',
            'NOTAccept-Encoding': 'ham',
            'NOTContent-Type': 'eggs'
         }
    monkeypatch.setattr('lib.consume_webservices.ConfigParser', BadCfgParser)
    parser = RequestConfigParser('whatever', THE_SERVICE)
    with pytest.raises(ConfigError) as err:
        parser.extract_headers()
    err_mess = str(err.value)
    for str_ in ['section', "'NOTAccept'", "'Accept'", THE_SERVICE]:
        assert str_ in err_mess



@pytest.mark.xfail
def test_extract_url_happy_path():
    assert False, 'code me'


@pytest.mark.xfail
def test_extract_url_sad_path():
    assert False, 'code me'


@pytest.mark.xfail
def test_form_data__format_happy_path():
    assert False, 'code me'


@pytest.mark.xfail
def test_form_data__format_sad_no_file_format():
    assert False, 'code me'


@pytest.mark.xfail
def test_form_data__format_sad_no_format_template():
    assert False, 'code me'


@pytest.mark.xfail
def test_reads_supplied_filename():
    assert False, 'code me'
