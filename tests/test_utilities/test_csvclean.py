#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvclean import CSVClean, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVClean(CSVKitTestCase, EmptyFileTests):
    Utility = CSVClean

    def assertCleaned(self, basename, output_lines, error_lines, additional_args=[]):
        args = ['examples/%s.csv' % basename] + additional_args
        output_file = six.StringIO()

        utility = CSVClean(args, output_file)
        utility.run()

        output_file.close()

        output_file = 'examples/%s_out.csv' % basename
        error_file = 'examples/%s_err.csv' % basename

        self.assertEqual(os.path.exists(output_file), bool(output_lines))
        self.assertEqual(os.path.exists(error_file), bool(error_lines))

        try:
            if output_lines:
                with open(output_file) as f:
                    for line in output_lines:
                        self.assertEqual(next(f), line)
                    self.assertRaises(StopIteration, next, f)
            if error_lines:
                with open(error_file) as f:
                    for line in error_lines:
                        self.assertEqual(next(f), line)
                    self.assertRaises(StopIteration, next, f)
        finally:
            if output_lines:
                os.remove(output_file)
            if error_lines:
                os.remove(error_file)

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/bad.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertCleaned('bad_skip_lines', [
            'column_a,column_b,column_c\n',
            '0,mixed types.... uh oh,17\n',
        ], [
            'line_number,msg,column_a,column_b,column_c\n',
            '1,"Expected 3 columns, found 4 columns",1,27,,I\'m too long!\n',
            '2,"Expected 3 columns, found 2 columns",,I\'m too short!\n',
        ], ['--skip-lines', '3'])

    def test_simple(self):
        self.assertCleaned('bad', [
            'column_a,column_b,column_c\n',
            '0,mixed types.... uh oh,17\n',
        ], [
            'line_number,msg,column_a,column_b,column_c\n',
            '1,"Expected 3 columns, found 4 columns",1,27,,I\'m too long!\n',
            '2,"Expected 3 columns, found 2 columns",,I\'m too short!\n',
        ])

    def test_no_header_row(self):
        self.assertCleaned('no_header_row', [
            '1,2,3\n',
        ], [])

    def test_removes_optional_quote_characters(self):
        self.assertCleaned('optional_quote_characters', [
            'a,b,c\n',
            '1,2,3\n',
        ], [])

    def test_changes_line_endings(self):
        self.assertCleaned('mac_newlines', [
            'a,b,c\n',
            '1,2,3\n',
            '"Once upon\n',
            'a time",5,6\n',
        ], [])

    def test_changes_character_encoding(self):
        self.assertCleaned('test_latin1', [
            'a,b,c\n',
            '1,2,3\n',
            '4,5,©\n',
        ], [], ['-e', 'latin1'])

    def test_dry_run(self):
        output = self.get_output_as_io(['-n', 'examples/bad.csv'])
        self.assertFalse(os.path.exists('examples/bad_err.csv'))
        self.assertFalse(os.path.exists('examples/bad_out.csv'))
        self.assertEqual(next(output)[:6], 'Line 1')
        self.assertEqual(next(output)[:6], 'Line 2')
