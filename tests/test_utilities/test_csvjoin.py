import os
import sys
import unittest
from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError
from csvkit.utilities.csvjoin import CSVJoin, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVJoin(CSVKitTestCase, EmptyFileTests):
    Utility = CSVJoin
    default_args = ['examples/dummy.csv', '-']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/join_a.csv', 'examples/join_b.csv']):
            launch_new_instance()

    def test_options(self):
        for args, message in (
            (
                ['-c' '1,2'],
                'The number of join column names must match the number of files, '
                'or be a single column name that exists in all files.',
            ),
            (['-c', '1', '--left', '--right'], 'It is not valid to specify both a left and a right join.'),
        ):
            with self.subTest(args=args):
                self.assertError(launch_new_instance, args, message)

    def test_join_options(self):
        for option in ('--left', '--right', '--outer'):
            with self.subTest(option=option):
                self.assertError(
                    launch_new_instance,
                    [option],
                    'You must provide join column names when performing an outer join.',
                )

    @unittest.skipIf(os.name != 'nt', 'Windows only')
    def test_glob(self):
        self.assertRows(['--no-inference', '-c', 'a', 'examples/dummy?.csv'], [
            ['a', 'b', 'c', 'b2', 'c2'],
            ['1', '2', '3', '2', '3'],
            ['1', '2', '3', '4', '5'],
        ])

    def test_sequential(self):
        output = self.get_output_as_io(['examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 4)

    def test_inner(self):
        output = self.get_output_as_io(['-c', 'a', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 3)

    def test_left(self):
        output = self.get_output_as_io(['-c', 'a', '--left', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 5)

    def test_right(self):
        output = self.get_output_as_io(['-c', 'a', '--right', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 4)

    def test_right_indices(self):
        output = self.get_output_as_io(['-c', '1,4', '--right', 'examples/join_a.csv', 'examples/blanks.csv'])
        self.assertEqual(len(output.readlines()), 2)

    def test_zero_based_first_column(self):
        self.assertRows(['--zero', '-c', '0', '--no-inference',
                         'examples/join_a.csv', 'examples/join_b.csv'], [
            ['a', 'b', 'c', 'b2', 'c2'],
            ['1', 'b', 'c', 'b', 'c'],
            ['1', 'b', 'c', 'b', 'c'],
        ])

    def test_zero_based_nonfirst_column(self):
        self.assertRows(['--zero', '-c', '1', '--no-inference',
                         'examples/join_a.csv', 'examples/join_b.csv'], [
            ['a', 'b', 'c', 'a2', 'c2'],
            *[[str(left), 'b', 'c', str(right), 'c'] for left in (1, 2, 3) for right in (1, 1, 4)],
        ])

    def test_zero_based_per_file_columns(self):
        self.assertRows(['--zero', '-c', '0,2,0', '--no-inference',
                         'examples/dummy.csv', 'examples/dummy_col_shuffled.csv', 'examples/dummy2.csv'], [
            ['a', 'b', 'c', 'b2', 'c2', 'b2_2', 'c2_2'],
            ['1', '2', '3', '2', '3', '2', '3'],
        ])

    def test_zero_based_outer_joins(self):
        paths = ['examples/join_a.csv', 'examples/join_b.csv']
        for option in ('--left', '--right', '--outer'):
            with self.subTest(option=option):
                expected = self.get_output(['--no-inference', '-c', 'a', option] + paths)
                self.assertEqual(self.get_output(['--no-inference', '--zero', '-c', '0', option] + paths), expected)

    def test_zero_based_column_bounds(self):
        with self.assertRaisesRegex(ColumnIdentifierError, "last column is 'c' at index 2"):
            self.get_output(['--zero', '-c', '3', 'examples/join_a.csv', 'examples/join_b.csv'])

    def test_default_and_named_join_columns(self):
        for args in (['-c', '1'], ['-c', 'a'], ['--zero', '-c', 'a']):
            self.assertRows(args + ['--no-inference', 'examples/join_a.csv', 'examples/join_b.csv'], [
                ['a', 'b', 'c', 'b2', 'c2'],
                ['1', 'b', 'c', 'b', 'c'],
                ['1', 'b', 'c', 'b', 'c'],
            ])

    def test_outer(self):
        output = self.get_output_as_io(['-c', 'a', '--outer', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 6)

    def test_left_short_columns(self):
        output = self.get_output_as_io(['-c', 'a', 'examples/join_a_short.csv', 'examples/join_b.csv'])
        with open('examples/join_short.csv') as f:
            self.assertEqual(output.readlines(), f.readlines())

    def test_single(self):
        self.assertRows(['examples/dummy.csv', '--no-inference'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_no_blanks(self):
        self.assertRows(['examples/blanks.csv', 'examples/blanks.csv'], [
            ['a', 'b', 'c', 'd', 'e', 'f', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2'],
            ['', '', '', '', '', '', '', '', '', '', '', ''],
        ])

    def test_blanks(self):
        self.assertRows(['--blanks', 'examples/blanks.csv', 'examples/blanks.csv'], [
            ['a', 'b', 'c', 'd', 'e', 'f', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2'],
            ['', 'NA', 'N/A', 'NONE', 'NULL', '.', '', 'NA', 'N/A', 'NONE', 'NULL', '.'],
        ])

    def test_no_header_row(self):
        output = self.get_output_as_io(
            ['-c', '1', '--no-header-row', 'examples/join_a.csv', 'examples/join_no_header_row.csv'])
        self.assertEqual(len(output.readlines()), 3)

    def test_no_inference(self):
        self.assertRows(['--no-inference', 'examples/join_a.csv', 'examples/join_short.csv'], [
            ['a', 'b', 'c', 'a2', 'b2', 'c2', 'b2_2', 'c2_2'],
            ['1', 'b', 'c', '1', 'b', '', 'b', 'c'],
            ['2', 'b', 'c', '1', 'b', '', 'b', 'c'],
            ['3', 'b', 'c', '', '', '', '', ''],
        ])

    def test_sniff_limit_no_limit(self):
        self.assertRows(['examples/join_a.csv', 'examples/sniff_limit.csv'], [
            ['a', 'b', 'c', 'a2', 'b2', 'c2'],
            ['1', 'b', 'c', 'True', '2', '3'],
            ['2', 'b', 'c', '', '', ''],
            ['3', 'b', 'c', '', '', ''],
        ])

    def test_sniff_limit_zero_limit(self):
        self.assertRows(['--snifflimit', '0', 'examples/join_a.csv', 'examples/sniff_limit.csv'], [
            ['a', 'b', 'c', 'a;b;c'],
            ['1', 'b', 'c', '1;2;3'],
            ['2', 'b', 'c', ''],
            ['3', 'b', 'c', ''],
        ])
