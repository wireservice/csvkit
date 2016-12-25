#!/usr/bin/env python

import sys

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

    def test_encoding(self):
        self.get_output(['-e', 'latin1', 'examples/test_latin1.csv'])

    def test_no_header_row(self):
        output = self.get_output(['-H', '-c', '2', 'examples/no_header_row.csv'])
        self.assertNotIn('1. a', output)
        self.assertIn('2. b', output)

    def test_count_only(self):
        output = self.get_output(['--count', 'examples/realdata/ks_1033_data.csv'])
        self.assertEqual(output, 'Row count: 1575\n')

    def test_unique(self):
        output = self.get_output(['-c', 'county', 'examples/realdata/ks_1033_data.csv'])
        self.assertIn('Unique values: 73\n', output)

    def test_max_length(self):
        output = self.get_output(['-c', 'county', 'examples/realdata/ks_1033_data.csv'])
        self.assertIn('Max length: 12\n', output)

    def test_freq_list(self):
        output = self.get_output(['examples/realdata/ks_1033_data.csv'])
        # print(output)
        self.assertIn('WYANDOTTE:\t123', output)
        self.assertIn('SALINE:\t59', output)
        self.assertNotIn('MIAMI:\t56', output)
