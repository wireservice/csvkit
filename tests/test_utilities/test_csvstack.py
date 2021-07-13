#!/usr/bin/env python

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvstack import CSVStack, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVStack(CSVKitTestCase, EmptyFileTests):
    Utility = CSVStack
    default_args = ['-']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertRows(['--skip-lines', '3', 'examples/test_skip_lines.csv', 'examples/test_skip_lines.csv'], [
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
