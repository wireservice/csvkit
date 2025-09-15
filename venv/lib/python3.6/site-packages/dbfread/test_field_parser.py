import datetime
from decimal import Decimal
from pytest import raises
from .field_parser import FieldParser

class MockHeader(object):
    dbversion = 0x02

class MockDBF(object):
    def __init__(self):
        self.header = MockHeader()
        self.encoding = 'ascii'
        self.char_decode_errors = 'strict'

class MockField(object):
    def __init__(self, type='', **kwargs):
        self.type = type
        self.__dict__.update(kwargs)

class MockMemoFile(dict):
    def __getitem__(self, index):
        if index == 0:
            return None
        else:
            return dict.__getitem__(self, index)

def make_field_parser(field_type, dbversion=0x02, memofile=None):
    dbf = MockDBF()
    dbf.header.dbversion = dbversion
    parser = FieldParser(dbf, memofile)
    field = MockField(field_type)

    def parse(data):
        return parser.parse(field, data)

    return parse

def test_0():
    parse = make_field_parser('0')

    assert parse(b'\0') == b'\x00'
    assert parse(b'\xaa\xff') == b'\xaa\xff'

def test_C():
    parse = make_field_parser('C')

    assert type(parse(b'test')) == type(u'')

def test_D():
    parse = make_field_parser('D')

    assert parse(b'00000000') is None
    assert parse(b'        ') is None

    epoch = datetime.date(1970, 1, 1)
    assert parse(b'19700101') == epoch

    with raises(ValueError):
        parse(b'NotIntgr')

def test_F():
    parse = make_field_parser('F')

    assert parse(b'') is None
    assert parse(b' ') is None

    assert parse(b'0') == 0
    assert parse(b'1') == 1
    assert parse(b'-1') == -1
    assert parse(b'3.14') == 3.14

    # In some files * is used for padding.
    assert parse(b'0.01**') == 0.01
    assert parse(b'******') is None

    with raises(ValueError):
        parse(b'jsdf')

# This also tests parse2B() (+)
def test_I():
    parse = make_field_parser('I')

    # Little endian unsigned integer.
    assert parse(b'\x00\x00\x00\x00') == 0
    assert parse(b'\x01\x00\x00\x00') == 1
    assert parse(b'\xff\xff\xff\xff') == -1

def test_L():
    parse = make_field_parser('L')

    for char in b'TtYy':
        assert parse(char) is True

    for char in b'FfNn':
        assert parse(char) is False

    for char in b'? ':
        assert parse(char) is None

    # Some invalid values.
    for char in b'!0':
        with raises(ValueError):
            parse(char)

# This also tests B, G and P.
def test_M():
    parse = make_field_parser('M', memofile=MockMemoFile({1: b'test'}))

    assert parse(b'\x01\x00\x00\x00') == u'test'
    assert parse(b'1') == u'test'
    assert parse(b'') is None
    with raises(ValueError):
        parse(b'NotInteger')

def test_B():
    # In VisualFox the B field is a double precision floating point number.
    parse = make_field_parser('B', dbversion=0x30)
    assert isinstance(parse(b'01abcdef'), float)
    assert parse(b'\0' * 8) == 0.0
    # Data must be exactly 8 bytes.
    with raises(Exception):
        parse(b'')
    
    # In other db versions it is a memo index.
    parse = make_field_parser('B', dbversion=0x02,
                              memofile=MockMemoFile({1: b'test'}))
    parse(b'1') == b'test'
    parse(b'') is None

def test_N():
    parse = make_field_parser('N')

    assert parse(b'') is None
    assert parse(b' ') is None
    assert parse(b'1') == 1
    assert parse(b'-99') == -99
    assert parse(b'3.14') == 3.14

    # In some files * is used for padding.
    assert parse(b'0.01**') == 0.01
    assert parse(b'******') is None

    with raises(ValueError):
        parse(b'okasd')

def test_O():
    """Test double field."""
    parse = make_field_parser('O')

    assert parse(b'\x00' * 8) == 0.0
    assert parse(b'\x00\x00\x00\x00\x00\x00\xf0?') == 1.0
    assert parse(b'\x00\x00\x00\x00\x00\x00Y\xc0') == -100

# This also tests parse40() (@)
def test_T():
    parse = make_field_parser('T')

    assert parse(b'') is None
    assert parse(b' ') is None

    # Todo: add more tests.

def test_Y():
    parse = make_field_parser('Y')

    assert parse(b'\1\0\0\0\0\0\0\0') == Decimal('0.0001')
    assert parse(b'\xff\xff\xff\xff\xff\xff\xff\xff') == Decimal('-0.0001')

def test_hex_field():
    class PlusFieldParser(FieldParser):
        encoding = 'latin1'

        def parse3F(self, field, data):
            """Parser for '?' field."""
            return None

    parser = PlusFieldParser(MockDBF())
    field = MockField('?')

    parser.parse(field, b'test')
