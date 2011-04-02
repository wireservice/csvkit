import unittest

from csvkit import convert

class TestConvert(unittest.TestCase):
    def test_no_file(self):
        self.assertRaises(ValueError, convert.convert, None, 'xls')

    def test_no_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, None)

    def test_invalid_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, 'INVALID')
