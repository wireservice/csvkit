#!/usr/bin/env python

import sys

import six

try:
    import unittest2 as unittest
    from mock import patch
except ImportError:
    import unittest
    from unittest.mock import patch

from csvkit.utilities.csvstat import CSVStat, launch_new_instance
from tests.utils import ColumnsTests, NamesTests


class TestCSVStat(unittest.TestCase, ColumnsTests, NamesTests):
    Utility = CSVStat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvstack', 'examples/dummy.csv']):
            launch_new_instance()

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

        self.assertFalse('A' in stats)
        self.assertTrue('B' in stats)

    def test_count_only(self):
        args = ['--count', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVStat(args, output_file)
        utility.main()

        stats = output_file.getvalue()

        self.assertEqual(stats, 'Row count: 1\n')
