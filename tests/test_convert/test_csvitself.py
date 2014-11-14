#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.convert import csvitself 

class TestCSVItself(unittest.TestCase):
    def test_csv_itself(self):
        with open('examples/testfixed_converted.csv', 'r') as f:
            contents = f.read()
            f.seek(0)
            self.assertEqual(contents, csvitself.csv2csv(f))
