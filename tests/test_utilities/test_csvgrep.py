#!/usr/bin/env python

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvgrep import CSVGrep, launch_new_instance
from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests


class TestCSVGrep(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVGrep
    default_args = ['-c', '1', '-m', '1']
    columns_args = ['-m', '1']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower()] + self.default_args + ['examples/dummy.csv']):
            launch_new_instance()

    def test_match(self):
        self.assertRows(['-c', '1', '-m', '1', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_no_match(self):
        self.assertRows(['-c', '1', '-m', 'NO MATCH', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
        ])

    def test_invert_match(self):
        self.assertRows(['-c', '1', '-i', '-m', 'NO MATCH', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_re_match(self):
        self.assertRows(['-c', '3', '-r', '^(3|9)$', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_string_match(self):
        self.assertRows(['-c', '1', '-m', 'ILLINOIS', 'examples/realdata/FY09_EDU_Recipients_by_State.csv'], [
            ['State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty', 'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance', 'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program', 'TOTAL', ''],
            ['ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''],
        ])

    def test_match_with_line_numbers(self):
        self.assertRows(['-c', '1', '-m', 'ILLINOIS', '-l', 'examples/realdata/FY09_EDU_Recipients_by_State.csv'], [
            ['line_numbers', 'State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty', 'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance', 'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program', 'TOTAL', ''],
            ['14', 'ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''],
        ])
