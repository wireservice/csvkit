from .field_parser import InvalidValue

def test_repr():
    assert repr(InvalidValue(b'')) == "InvalidValue(b'')"

def test_type():
    assert isinstance(InvalidValue(b''), bytes)
