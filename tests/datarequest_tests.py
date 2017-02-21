
from lib.consume_webservices import DataRequest


MOCK_FORMAT = 'wibble'
MOCK_URL = 'https://www.example.com'
MOCK_HEADERS = {}
class MockConfig():
    def form_data__format(_):
        return MOCK_FORMAT
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)
    def extract_headers(_):
        return MOCK_HEADERS
    def extract_url(_):
        return MOCK_URL

def test_construction_empty():
    """
    Can we create a DataRequest with no args?
    does it know it is not yet fit to send?
    """
    req = DataRequest()
    assert req.headers == {}
    assert req.form_data == {}
    assert req.url == ''
    assert not req.can_send


def test_construction_valid_from_args():
    """
    Can we create a DataRequest with passing
    some args and have it know it is fit to send?
    """
    heads = {'Accept': 'Thorough the fog it came'}
    url = 'https://www.diomedeidae.com'
    formdata = {'datasets': 'an albatross', 'format': 'xml/x-seabird'}
    req = DataRequest(url, heads, formdata)
    assert req.headers == heads
    assert req.form_data == formdata
    assert req.url == url
    assert req.can_send


def test_read_url():
    """
    test the `read_url` method
    overwrites url param with
    values parsed from a config file
    """
    req = DataRequest(url='not a real url')
    assert req.url == 'not a real url'
    req.read_url(MockConfig())
    assert req.url == MOCK_URL


def test_read_headers():
    """
    test the `read_headers` method
    can overwrite `headers` param
    based on parsed config file values
    """
    req = DataRequest(headers={'accept': 'nothing'})
    assert req.headers.get('accept') == 'nothing'
    req.read_headers(MockConfig())
    assert req.headers == MOCK_HEADERS


def test_read_attributes():
    """
    test the `read_attributes` method
    can overwrite `headers` and `url` params
    based on parsed config file values
    """
    req = DataRequest(url='not a real url', headers={'accept': 'nothing'})
    assert req.headers.get('accept') == 'nothing'
    assert req.url == 'not a real url'
    req.read_attributes(MockConfig())
    assert req.headers == MOCK_HEADERS
    assert req.url == MOCK_URL
