import unittest

from csvkit import convert

class TestConvert(unittest.TestCase):
    def test_valid_file(self):
        with open('examples/test.xls', 'r') as f:
            output = convert.convert(f, 'xls')
        
        with open('examples/testxls_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
            
    def test_no_file(self):
        self.assertRaises(ValueError, convert.convert, None, 'xls')

    def test_no_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, None)

    def test_invalid_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, 'INVALID')
