#!/usr/bin/env python

import six

if six.PY3:
    from io import StringIO
else:
    from cStringIO import StringIO

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvstat import CSVStat

class TestCSVStat(unittest.TestCase):
    def test_runs(self):
        args = ['examples/dummy.csv']
        output_file = StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

