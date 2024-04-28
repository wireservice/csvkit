import io
import os
import sys
from unittest.mock import patch

import agate

from csvkit.utilities.csvclean import CSVClean, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVClean(CSVKitTestCase, EmptyFileTests):
    Utility = CSVClean

    def tearDown(self):
        output_file = "stdin_out.csv"
        if os.path.isfile(output_file):
            os.remove(output_file)

    def assertCleaned(self, args, output_rows, error_rows=[]):
        output_file = io.StringIO()
        error_file = io.StringIO()

        utility = CSVClean(args, output_file, error_file)

        if error_rows:
            with self.assertRaises(SystemExit) as e:
                utility.run()

            self.assertEqual(e.exception.code, 1)
        else:
            utility.run()

        output_file.seek(0)
        error_file.seek(0)

        if output_rows:
            reader = agate.csv.reader(output_file)
            for row in output_rows:
                self.assertEqual(next(reader), row)
            self.assertRaises(StopIteration, next, reader)
        if error_rows:
            reader = agate.csv.reader(error_file)
            for row in error_rows:
                self.assertEqual(next(reader), row)
            self.assertRaises(StopIteration, next, reader)

        output_file.close()
        error_file.close()

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertCleaned(['--skip-lines', '3', 'examples/bad_skip_lines.csv'], [
            ['column_a', 'column_b', 'column_c'],
            ['0', 'mixed types.... uh oh', '17'],
        ], [
            ['line_number', 'msg', 'column_a', 'column_b', 'column_c'],
            ['1', 'Expected 3 columns, found 4 columns', '1', '27', '', "I'm too long!"],
            ['2', 'Expected 3 columns, found 2 columns', '', "I'm too short!"],
        ])

    def test_simple(self):
        self.assertCleaned(['examples/bad.csv'], [
            ['column_a', 'column_b', 'column_c'],
            ['0', 'mixed types.... uh oh', '17'],
        ], [
            ['line_number', 'msg', 'column_a', 'column_b', 'column_c'],
            ['1', 'Expected 3 columns, found 4 columns', '1', '27', '', "I'm too long!"],
            ['2', 'Expected 3 columns, found 2 columns', '', "I'm too short!"],
        ])

    def test_no_header_row(self):
        self.assertCleaned(['examples/no_header_row.csv'], [
            ['1', '2', '3'],
        ], [])

    def test_header_normalize_space(self):
        self.assertCleaned(['--header-normalize-space', 'examples/test_header_newline.csv'], [
            ['start end', 'b', 'c'],
            ['d', 'e', 'f'],
        ], [])

    def test_removes_optional_quote_characters(self):
        self.assertCleaned(['examples/optional_quote_characters.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_changes_line_endings(self):
        self.assertCleaned(['examples/mac_newlines.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['Once upon\na time', '5', '6'],
        ])

    def test_changes_character_encoding(self):
        self.assertCleaned(['-e', 'latin1', 'examples/test_latin1.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['4', '5', u'©'],
        ])

    def test_removes_bom(self):
        self.assertCleaned(['examples/test_utf8_bom.csv'], [
            ['foo', 'bar', 'baz'],
            ['1', '2', '3'],
            ['4', '5', 'ʤ'],
        ])
