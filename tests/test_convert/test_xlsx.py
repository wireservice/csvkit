#!/usr/bin/env python

import unittest

from csvkit.convert import xlsx

class TestXLSX(unittest.TestCase):
    def test_xlsx(self):
        with open('examples/test.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f)

        with open('examples/testxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

