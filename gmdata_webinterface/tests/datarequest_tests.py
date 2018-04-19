"""test building up a request to a Geomag data webservice"""
import pytest
import requests

from gmdata_webinterface.consume_webservices import DataRequest, InvalidRequest, check_response


MOCK_FORMAT = 'wibble'
MOCK_URL = 'https://www.example.com'
MOCK_HEADERS = {'mock': 'header'}


# small Mock classes can be weird
# pylint: disable=missing-docstring, too-few-public-methods, no-self-use
class MockConfig(object):
    url = MOCK_URL
    headers = MOCK_HEADERS

    def form_data__format(self):
        return MOCK_FORMAT


# requests internals make linting unhappy
# pylint: disable=no-member
class MockResponse(object):
    status_code = requests.codes.ok
    raise_for_status = requests.models.Response.raise_for_status
    reason = 'OK'


class SpyRequests(object):
    post_call_count = 0
    post_called_with = 'not a request'

    @classmethod
    def post(cls, url, data, headers):
        cls.post_call_count += 1
        cls.post_called_with = {
            'url': url, 'headers': headers, 'data': data
            }
        return MockResponse()

    @classmethod
    def reset(cls):
        cls.post_call_count = 0
        cls.post_called_with = 'not a request'
# pylint: enable=no-member, missing-docstring, too-few-public-methods, no-self-use


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


def test_sending_request_happy_path(monkeypatch):
    """
    if we've built a valid request, can we send
    it?
    """
    SpyRequests.reset()
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.rq', SpyRequests)
    req = DataRequest()
    req.read_attributes(MockConfig())
    req.set_form_data({'format': MOCK_FORMAT, 'datasets': 'wibble'})
    assert SpyRequests.post_call_count == 0
    req.send()
    assert SpyRequests.post_call_count == 1
    print(SpyRequests.post_called_with)


#  long test names are OK
def test_cannot_send_until_all_parts_populated(monkeypatch):  # pylint: disable=invalid-name
    """
    if we do not have a complete DataRequest,
    we should not be able to send it.

    We'll create an empty `DataRequest` and
    slowly populate it, checking at each stage
    that it cannot be sent until it is full
    """
    SpyRequests.reset()
    monkeypatch.setattr('gmdata_webinterface.consume_webservices.rq', SpyRequests)
    config = MockConfig()

    assert SpyRequests.post_call_count == 0
    req = DataRequest()
    with pytest.raises(InvalidRequest) as err:
        req.send()
    err_mess = str(err.value)
    for method in ['read_url', 'read_headers', 'set_form_data']:
        assert method in err_mess
    assert SpyRequests.post_call_count == 0

    req.read_headers(config)
    with pytest.raises(InvalidRequest) as err:
        req.send()
    err_mess = str(err.value)
    for method in ['read_url', 'set_form_data']:
        assert method in err_mess
    assert 'read_headers' not in err_mess
    assert SpyRequests.post_call_count == 0

    req.read_url(config)
    with pytest.raises(InvalidRequest) as err:
        req.send()
    err_mess = str(err.value)
    assert 'set_form_data' in err_mess
    for method in ['read_url', 'read_headers']:
        assert method not in err_mess
    assert SpyRequests.post_call_count == 0

    req.set_form_data({'some': 'data'})
    # now everthing is set we should be able to send
    #  without raising an error
    resp = req.send()
    assert SpyRequests.post_call_count == 1
    assert resp.status_code == MockResponse.status_code


def test_sending_request_404_response_raises(monkeypatch):    # pylint: disable=invalid-name
    """
    if we've built a request,
    sent it but got a 404 error response,
    do we raise the appropriate error?
    """
# these small Mock classes are better short and a bit weird
# pylint: disable=no-member, missing-docstring, too-few-public-methods, no-method-argument
    class Mock404(object):
        status_code = requests.codes.not_found
        reason = 'Not Found'
        url = MOCK_URL

        raise_for_status = requests.models.Response.raise_for_status

    class Mock404Responder(object):
        def post(**kwargs):
            return Mock404()
# pylint: enable=no-member, missing-docstring, too-few-public-methods, no-method-argument

    monkeypatch.setattr('gmdata_webinterface.consume_webservices.rq', Mock404Responder)
    req = DataRequest()
    req.read_attributes(MockConfig())
    req.set_form_data({'some': 'data'})
    with pytest.raises(requests.exceptions.HTTPError):
        req.send()


def test_check_response_raises():    # pylint: disable=invalid-name
    """
    check we get the expected failures when a response isn't 'ok'
    """
    with pytest.raises(ValueError) as error:
        check_response(requests.codes.internal_server_error, '')
    assert '500' in error.value.args[0]

    # example bytes for empty zip file return in response.content
    empty_zip_bytes = b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    with pytest.raises(ValueError) as error:
        check_response(requests.codes.ok, empty_zip_bytes)
    assert 'no valid files returned' in error.value.args[0]


def test_construction_valid_from_args():  # pylint: disable=invalid-name
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


def test_set_form_data_config():
    """
    Can we set and reset form_data
    from dict?
    """
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
