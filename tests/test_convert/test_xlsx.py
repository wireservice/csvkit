#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.convert import xlsx
from datetime import datetime

class TestXLSX(unittest.TestCase):
    def test_xlsx(self):
        with open('examples/test.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f)

        with open('examples/testxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

    def test_xlsx_with_sheet(self):
        with open('examples/sheets.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f, None, sheet='Sheet2')

        with open('examples/sheetsxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

    def test_normalize_datetime(self):
        dt = datetime(2013, 8, 22, 9, 51, 59, 999001)
        self.assertEqual(datetime(2013, 8, 22, 9, 52, 0), xlsx.normalize_datetime(dt))

        dt = datetime(2013, 8, 22, 9, 51, 58, 999001)
        self.assertEqual(datetime(2013, 8, 22, 9, 51, 59), xlsx.normalize_datetime(dt))

        dt = datetime(2013, 8, 22, 9, 51, 59, 0)
        self.assertEqual(dt, xlsx.normalize_datetime(dt))

        dt = datetime(2013, 8, 22, 9, 51, 59, 999)
        self.assertEqual(datetime(2013, 8, 22, 9, 51, 59, 0), xlsx.normalize_datetime(dt))

        dt = datetime(2013, 8, 22, 9, 51, 59, 5000)
        self.assertEqual(dt, xlsx.normalize_datetime(dt))

