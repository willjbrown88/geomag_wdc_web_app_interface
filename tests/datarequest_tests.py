
from lib.consume_webservices import DataRequest


MOCK_FORMAT = 'wibble'
MOCK_URL = 'https://www.example.com'
MOCK_HEADERS = {'mock': 'header'}
class MockConfig():
    def form_data__format(_):
        return MOCK_FORMAT
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
    can overwrite both `headers` and `url` params
    based on parsed config file values
    """
    req = DataRequest(url='not a real url', headers={'accept': 'nothing'})
    assert req.headers.get('accept') == 'nothing'
    assert req.url == 'not a real url'
    req.read_attributes(MockConfig())
    assert req.headers == MOCK_HEADERS
    assert req.url == MOCK_URL


def test_set_form_data():
    """does the `set_form_data` do what it says on the tin?"""
    empty_at_1st = DataRequest()
    assert empty_at_1st.form_data == {}
    empty_at_1st.set_form_data({'walrus': 'power'})
    assert empty_at_1st.form_data['walrus'] == 'power'
    populated_at_1st = DataRequest(form_data={'walrus': 'power'})
    assert populated_at_1st.form_data['walrus'] == 'power'
    populated_at_1st.set_form_data({'narwhal': 'tusk'})
    assert populated_at_1st.form_data['narwhal'] == 'tusk'


def test_can_send():
    """can send should only work with fully populated instance"""
    empty_at_1st = DataRequest()
    assert not empty_at_1st.can_send
    config = MockConfig()
    empty_at_1st.read_headers(config)
    assert not empty_at_1st.can_send
    empty_at_1st.read_url(config)
    assert not empty_at_1st.can_send
    empty_at_1st.set_form_data({'some': 'data'})
    assert empty_at_1st.can_send
