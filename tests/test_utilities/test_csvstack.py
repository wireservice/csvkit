import os
import sys
import unittest
from unittest.mock import patch

from csvkit.utilities.csvstack import CSVStack, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVStack(CSVKitTestCase, EmptyFileTests):
    Utility = CSVStack
    default_args = ['-']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_options(self):
        self.assertError(
            launch_new_instance,
            ['-g', '1,2'],
            'The number of grouping values must be equal to the number of CSV files being stacked.',
        )

    @unittest.skipIf(os.name != 'nt', 'Windows only')
    def test_glob(self):
        self.assertRows(['examples/dummy*.csv'], [
            ['a', 'b', 'c', 'd'],
            ['1', '2', '3', ''],
            ['1', '2', '3', ''],
            ['1', '2', '3', ''],
            ['1', '4', '5', ''],
            ['1', '2', '3', ''],
            ['1', '2', '3', '4'],
        ])

    def test_skip_lines(self):
        self.assertRows(['--skip-lines', '3', 'examples/test_skip_lines.csv', 'examples/test_skip_lines.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['1', '2', '3'],
        ])

    def test_skip_lines_stdin(self):
        with open('examples/test_skip_lines.csv', 'rb') as f, stdin_as_string(f):
            self.assertRows(['--skip-lines', '3', '-', 'examples/test_skip_lines.csv'], [
                ['a', 'b', 'c'],
                ['1', '2', '3'],
                ['1', '2', '3'],
            ])

    def test_single_file_stack(self):
        self.assertRows(['examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_multiple_file_stack(self):
        self.assertRows(['examples/dummy.csv', 'examples/dummy2.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['1', '2', '3'],
        ])

    def test_multiple_file_stack_col(self):
        self.assertRows(['examples/dummy.csv', 'examples/dummy_col_shuffled.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['1', '2', '3'],
        ])

        self.assertRows(['examples/dummy_col_shuffled.csv', 'examples/dummy.csv'], [
            ['b', 'c', 'a'],
            ['2', '3', '1'],
            ['2', '3', '1'],
        ])

    def test_multiple_file_stack_col_ragged(self):
        self.assertRows(['examples/dummy.csv', 'examples/dummy_col_shuffled_ragged.csv'], [
            ['a', 'b', 'c', 'd'],
            ['1', '2', '3', ''],
            ['1', '2', '3', '4'],
        ])

    def test_multiple_file_stack_col_ragged_stdin(self):
        with open('examples/dummy.csv', 'rb') as f, stdin_as_string(f):
            self.assertRows(['-', 'examples/dummy_col_shuffled_ragged.csv'], [
                ['a', 'b', 'c', 'd'],
                ['1', '2', '3', ''],
                ['1', '2', '3', '4'],
            ])

        with open('examples/dummy.csv', 'rb') as f, stdin_as_string(f):
            self.assertRows(['examples/dummy_col_shuffled_ragged.csv', '-'], [
                ['b', 'c', 'a', 'd'],
                ['2', '3', '1', '4'],
                ['2', '3', '1', ''],
            ])

    def test_explicit_grouping(self):
        self.assertRows(['--groups', 'asd,sdf', '-n', 'foo', 'examples/dummy.csv', 'examples/dummy2.csv'], [
            ['foo', 'a', 'b', 'c'],
            ['asd', '1', '2', '3'],
            ['sdf', '1', '2', '3'],
        ])

    def test_filenames_grouping(self):
        self.assertRows(['--filenames', '-n', 'path', 'examples/dummy.csv', 'examples/dummy2.csv'], [
            ['path', 'a', 'b', 'c'],
            ['dummy.csv', '1', '2', '3'],
            ['dummy2.csv', '1', '2', '3'],
        ])


class TestNoHeaderRow(TestCSVStack):

    def test_no_header_row_basic(self):
        self.assertRows(['--no-header-row', 'examples/no_header_row.csv', 'examples/no_header_row2.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['4', '5', '6'],
        ])

    def test_no_header_row_basic_stdin(self):
        with open('examples/no_header_row.csv', 'rb') as f, stdin_as_string(f):
            self.assertRows(['--no-header-row', '-', 'examples/no_header_row2.csv'], [
                ['a', 'b', 'c'],
                ['1', '2', '3'],
                ['4', '5', '6'],
            ])

        with open('examples/no_header_row.csv', 'rb') as f, stdin_as_string(f):
            self.assertRows(['--no-header-row', 'examples/no_header_row2.csv', '-'], [
                ['a', 'b', 'c'],
                ['4', '5', '6'],
                ['1', '2', '3'],
            ])

    def test_grouped_manual_and_named_column(self):
        self.assertRows(
            [
                "--no-header-row",
                "--groups",
                "foo,bar",
                "-n",
                "hey",
                "examples/dummy.csv",
                "examples/dummy3.csv",
            ],
            [
                ["hey", "a", "b", "c"],
                ["foo", "a", "b", "c"],
                ["foo", "1", "2", "3"],
                ["bar", "a", "b", "c"],
                ["bar", "1", "2", "3"],
                ["bar", "1", "4", "5"],
            ],
        )

    def test_grouped_filenames(self):
        self.assertRows(
            [
                "-H",
                "--filenames",
                "examples/no_header_row.csv",
                "examples/no_header_row2.csv",
            ],
            [
                ["group",                "a", "b", "c"],
                ["no_header_row.csv",    "1", "2", "3"],
                ["no_header_row2.csv",   "4", "5", "6"],
            ],
        )

    def test_grouped_filenames_and_named_column(self):
        self.assertRows(
            [
                "-H",
                "--filenames",
                "-n",
                "hello",
                "examples/no_header_row.csv",
                "examples/no_header_row2.csv",
            ],
            [
                ["hello", "a", "b", "c"],
                ["no_header_row.csv", "1", "2", "3"],
                ["no_header_row2.csv", "4", "5", "6"],
            ],
        )
