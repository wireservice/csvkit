#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.convert import xls

class TestXLS(unittest.TestCase):
    def test_xls(self):
        with open('examples/test.xls', 'rb') as f:
            output = xls.xls2csv(f)

        with open('examples/testxls_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

    def test_xls_with_sheet(self):
        with open('examples/sheets.xls', 'rb') as f:
            output = xls.xls2csv(f, sheet='Sheet2')

        with open('examples/sheetsxls_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
