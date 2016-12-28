#!/usr/bin/env python

import sys

import agate

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvstat import CSVStat, launch_new_instance
from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests


class TestCSVStat(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVStat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        self.get_output(['examples/test_utf8.csv'])

    def test_columns(self):
        output = self.get_output(['-c', '2', 'examples/testxls_converted.csv'])
        self.assertNotIn('1. "text"', output)
        self.assertIn('2. "date"', output)

    def test_encoding(self):
        self.get_output(['-e', 'latin1', 'examples/test_latin1.csv'])

    def test_no_header_row(self):
        output = self.get_output(['-H', '-c', '2', 'examples/no_header_row.csv'])
        self.assertNotIn('1. "a"', output)
        self.assertIn('2. "b"', output)

    def test_count_only(self):
        output = self.get_output(['--count', 'examples/realdata/ks_1033_data.csv'])
        self.assertEqual(output, 'Row count: 1575\n')

    def test_unique(self):
        output = self.get_output(['-c', 'county', 'examples/realdata/ks_1033_data.csv'])
        self.assertRegex(output, r'Unique values:\s+73')

    def test_max_length(self):
        output = self.get_output(['-c', 'county', 'examples/realdata/ks_1033_data.csv'])
        self.assertRegex(output, r'Longest value:\s+12')

    def test_freq_list(self):
        output = self.get_output(['examples/realdata/ks_1033_data.csv'])

        self.assertIn('WYANDOTTE (123x)', output)
        self.assertIn('SALINE (59x)', output)
        self.assertNotIn('MIAMI (56x)', output)

    def test_csv(self):
        output = self.get_output_as_io(['--csv', 'examples/realdata/ks_1033_data.csv'])

        reader = agate.csv.reader(output)

        header = next(reader)

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[4], 'unique')

        row = next(reader)

        self.assertEqual(row[1], 'state')
        self.assertEqual(row[2], 'Text')
        self.assertEqual(row[5], '')
        self.assertEqual(row[11], '2')

    def test_csv_columns(self):
        output = self.get_output_as_io(['--csv', '-c', '4', 'examples/realdata/ks_1033_data.csv'])

        reader = agate.csv.reader(output)

        header = next(reader)

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[4], 'unique')

        row = next(reader)

        self.assertEqual(row[1], 'nsn')
        self.assertEqual(row[2], 'Text')
        self.assertEqual(row[5], '')
        self.assertEqual(row[11], '16')
