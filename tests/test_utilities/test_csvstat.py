#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit.utilities.csvstat import CSVStat

class TestCSVStat(unittest.TestCase):
    def test_runs(self):
        args = ['examples/dummy.csv']
        output_file = StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

