#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvstat import CSVStat

class TestCSVStat(unittest.TestCase):
    def test_runs(self):
        args = ['examples/test_utf8.csv']
        output_file = six.StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

    def test_encoding(self):
        args = ['-e', 'latin1', 'examples/test_latin1.csv']
        output_file = six.StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

    def test_no_header_row(self):
        args = ['-H', '-c', '2', 'examples/no_header_row.csv']
        output_file = six.StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

        stats = output_file.getvalue()

        self.assertFalse('column1' in stats)
        self.assertTrue('column2' in stats)

    def test_count_only(self):
        args = ['--count', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

        stats = output_file.getvalue()

        self.assertEqual(stats, 'Row count: 1\n')

