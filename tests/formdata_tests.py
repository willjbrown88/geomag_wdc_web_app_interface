"""test container class for POST request form data"""
from datetime import date
import pytest

from lib.consume_webservices import FormData

# tiny Mock helper classes are OK being weird
# pylint: disable=too-few-public-methods, missing-docstring
MOCK_FORMAT = 'wibble'
class MockConfig(object):
    dataformat = MOCK_FORMAT
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

# pylint: enable=too-few-public-methods, missing-docstring

def test_construction():
    """
    can we instantiate a FormData obj?
    expect it to get 'format' from passed config
    """
    formdata = FormData(MockConfig())
    assert formdata.format == MOCK_FORMAT
    assert formdata.datasets is None


def test_repr_str_eq():
    """
    do we pretty print stuff,
    eval to new instance sensibly
    and test for equality
    """
    original = FormData(MockConfig())
    via_repr = eval(repr(original))  # pylint: disable=eval-used; OK for repr testing
    assert original == via_repr
    via_repr.format = "don't monkey patch in production folks"
    assert original != via_repr

    str_rep = str(original)
    assert 'FormData' in str_rep
    assert 'datasets' in str_rep
    assert 'format' in str_rep
    # expecting a dict
    assert '{' in str_rep


HOURLY_DATASET_ARGS = {
    'start_date': date(1999, 12, 31),
    'end_date': date(2000, 1, 2),
    'station': 'XXX',
    'cadence': 'hour',
    'service': 'YYY'
}


def test_set_datasets_hourly():
    """form the expected pattern of hour cadence datasets"""
    formdata = FormData(MockConfig())
    assert formdata.datasets is None
    # unpack so don't overwrite 'constant'
    formdata.set_datasets(**HOURLY_DATASET_ARGS)
    assert 'yyy/datasets/hour' in formdata.datasets
    assert 'xxx1999' in formdata.datasets
    assert 'xxx2000' in formdata.datasets


def test_set_datasets_minutely():
    """form the expected pattern of minute cadence datasets"""
    formdata = FormData(MockConfig())
    minutely_args = {**HOURLY_DATASET_ARGS}
    minutely_args['cadence'] = 'minute'
    formdata.set_datasets(**minutely_args)
    assert 'yyy/datasets/minute' in formdata.datasets
    assert 'xxx199912' in formdata.datasets
    assert 'xxx200001' in formdata.datasets


def test_set_datasets_bad_cadence():
    """form the expected pattern of minute cadence datasets"""
    formdata = FormData(MockConfig())
    bad_cadence = {**HOURLY_DATASET_ARGS}
    bad_cadence['cadence'] = 'wibble'
    with pytest.raises(ValueError) as err:
        formdata.set_datasets(**bad_cadence)
    err_mess = str(err.value)
    for str_ in ['hour', 'minute', 'wibble']:
        assert str_ in err_mess


def test_as_dict():
    """
    do we get back the datasets and formats as expected?
    and the `as_dict` meth should fail before
    we call `set_datasets`
    """
    formdata = FormData(MockConfig())
    with pytest.raises(ValueError) as err:
        formdata.as_dict()
    assert 'set_datasets' in str(err.value)
    formdata.set_datasets(**HOURLY_DATASET_ARGS)
    payload_dict = formdata.as_dict()
    assert 'datasets' in payload_dict.keys()
    assert payload_dict.get('format') == MOCK_FORMAT
