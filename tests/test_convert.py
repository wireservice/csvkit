from csvkit import convert

import unittest

class TestGuessFormat(unittest.TestCase):
    def test_fixed(self):
        format = convert.guess_format('testdata')
        self.assertEqual(format, 'fixed')

    def test_xls(self):
        format = convert.guess_format('testdata.xls')
        self.assertEqual(format, 'xls')

    def test_xlsx(self):
        format = convert.guess_format('testdata.xlsx')
        self.assertEqual(format, 'xlsx')

class TestConvert(unittest.TestCase):
    def test_no_file(self):
        self.assertRaises(ValueError, convert.convert, None, 'xls')

    def test_no_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, None)

    def test_invalid_format(self):
        with open('examples/dummy.csv', 'r') as f:
            self.assertRaises(ValueError, convert.convert, f, 'INVALID')

class TestFixed(unittest.TestCase):
    def test_fixed(self):
        with open('examples/testfixed', 'r') as f:
            with open('examples/testfixed_schema.csv', 'r') as schema:
                output = convert.fixed2csv(f, schema)
        
        with open('examples/testfixed_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
