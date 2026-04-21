import json
import sys
from unittest.mock import patch

import agate

from csvkit.utilities.csvstat import CSVStat, launch_new_instance
from tests.utils import ColumnsTests, CSVKitTestCase, EmptyFileTests, NamesTests


class TestCSVStat(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVStat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_options(self):
        self.assertError(
            launch_new_instance,
            ['--min', '--max'],
            'Only one operation argument may be specified (--mean, --median, etc).',
        )

    def test_format_options(self):
        for option in ('csv', 'json', 'count'):
            with self.subTest(option=option):
                self.assertError(
                    launch_new_instance,
                    ['--min', f'--{option}'],
                    f'You may not specify --{option} and an operation (--mean, --median, etc) at the same time.',
                )

    def test_runs(self):
        # Test that csvstat doesn't error on UTF-8 input.
        self.get_output(['examples/test_utf8.csv'])

    def test_encoding(self):
        # Test that csvstat doesn't error on Latin-1 input.
        self.get_output(['-e', 'latin1', 'examples/test_latin1.csv'])

    def test_columns(self):
        output = self.get_output(['-c', '2', 'examples/testxls_converted.csv'])
        self.assertNotIn('1. "text"', output)
        self.assertIn('2. "date"', output)

    def test_linenumbers(self):
        output = self.get_output(['-c', '2', '--linenumbers', 'examples/dummy.csv'])
        self.assertNotIn('1. "a"', output)
        self.assertIn('2. "b"', output)

    def test_no_header_row(self):
        output = self.get_output(['-c', '2', '--no-header-row', 'examples/no_header_row.csv'])
        self.assertNotIn('1. "a"', output)
        self.assertIn('2. "b"', output)

    def test_count_only(self):
        output = self.get_output(['--count', 'examples/realdata/ks_1033_data.csv'])
        self.assertEqual(output, '1575\n')

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

    def test_freq(self):
        output = self.get_output(['examples/realdata/ks_1033_data.csv', '--freq'])

        self.assertIn('  1. state: { "KS": 1575 }', output)

    def test_freq_count(self):
        output = self.get_output(['examples/realdata/ks_1033_data.csv', '--freq-count', '1'])

        self.assertIn('WYANDOTTE (123x)', output)
        self.assertNotIn('FINNEY (103x)', output)
        self.assertNotIn('MIAMI (56x)', output)

    def test_csv(self):
        output = self.get_output_as_io(['--csv', 'examples/realdata/ks_1033_data.csv'])

        reader = agate.csv.reader(output)

        header = next(reader)

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[5], 'unique')

        row = next(reader)

        self.assertEqual(row[1], 'state')
        self.assertEqual(row[2], 'Text')
        self.assertEqual(row[6], '')
        self.assertEqual(row[12], '2')

    def test_csv_columns(self):
        output = self.get_output_as_io(['--csv', '-c', '4', 'examples/realdata/ks_1033_data.csv'])

        reader = agate.csv.reader(output)

        header = next(reader)

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[5], 'unique')

        row = next(reader)

        self.assertEqual(row[1], 'nsn')
        self.assertEqual(row[2], 'Text')
        self.assertEqual(row[6], '')
        self.assertEqual(row[12], '16')

    def test_json(self):
        output = self.get_output_as_io(['--json', 'examples/realdata/ks_1033_data.csv'])

        data = json.load(output)

        header = list(data[0])

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[5], 'unique')

        row = list(data[0].values())

        self.assertEqual(row[1], 'state')
        self.assertEqual(row[2], 'Text')
        self.assertNotIn('min', data[0])
        self.assertEqual(row[-2], 2.0)

    def test_json_columns(self):
        output = self.get_output_as_io(['--json', '-c', '4', 'examples/realdata/ks_1033_data.csv'])

        data = json.load(output)

        header = list(data[0])

        self.assertEqual(header[1], 'column_name')
        self.assertEqual(header[5], 'unique')

        row = list(data[0].values())

        self.assertEqual(row[1], 'nsn')
        self.assertEqual(row[2], 'Text')
        self.assertNotIn('min', data[0])
        self.assertEqual(row[-2], 16.0)

    def test_decimal_format(self):
        output = self.get_output(['-c', 'TOTAL', '--mean', 'examples/realdata/FY09_EDU_Recipients_by_State.csv'])

        self.assertEqual(output, '9,748.346\n')

        output = self.get_output([
            '-c', 'TOTAL', '--mean', '--no-grouping-separator', 'examples/realdata/FY09_EDU_Recipients_by_State.csv',
        ])

        self.assertEqual(output, '9748.346\n')

        output = self.get_output([
            '-c', 'TOTAL', '--mean', '--decimal-format', '%.2f', 'examples/realdata/FY09_EDU_Recipients_by_State.csv',
        ])

        self.assertEqual(output, '9,748.35\n')
