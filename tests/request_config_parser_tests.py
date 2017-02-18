import configparser
import pytest
from lib.consume_webservices import RequestConfigParser, ConfigError

THE_SERVICE = 'ABC'
class MockCfgParser(object):
    """
    fake the bits we need of
    std lib's configparser.ConfigParser
    """
    data = {
        'Accept': 'spam',
        'Accept-Encoding': 'ham',
        'Content-Type': 'eggs',
        'FileFormat': 'beep',
        'Hostname': 'foo',
        'Route': 'bar',
        '_format_template': 'baz'
    }
    def read(self, _):
        return None
    def sections(_):
        return [THE_SERVICE]
    def get(self, _, key):
        return self.data.get(key)

def test_construction(monkeypatch):
    monkeypatch.setattr('lib.consume_webservices.ConfigParser', MockCfgParser)
    got = RequestConfigParser('afile', THE_SERVICE)
    assert got.service == THE_SERVICE
    with pytest.raises(ConfigError) as err:
        got = RequestConfigParser('afile', 'Wally the service')