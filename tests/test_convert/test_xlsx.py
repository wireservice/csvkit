#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.convert import xlsx

class TestXLSX(unittest.TestCase):
    def test_xlsx(self):
        with open('examples/test.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f)

        with open('examples/testxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

    def test_xlsx_with_sheet(self):
        with open('examples/sheets.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f, sheet='Sheet2')

        with open('examples/sheetsxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
