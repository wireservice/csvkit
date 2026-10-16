import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from csvkit.utilities.csvgrep import CSVGrep, launch_new_instance
from tests.utils import ColumnsTests, CSVKitTestCase, EmptyFileTests, NamesTests


class TestCSVGrep(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVGrep
    default_args = ['-c', '1', '-m', '1']
    columns_args = ['-m', '1']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower()] + self.default_args + ['examples/dummy.csv']):
            launch_new_instance()

    def test_options(self):
        for args, message in (
            ([], 'You must specify at least one column to search using the -c option.'),
            (['-c', '1'], 'One of -r, -m or -f must be specified, unless using the -n option.'),
        ):
            with self.subTest(args=args):
                self.assertError(launch_new_instance, args, message)

    def test_skip_lines(self):
        self.assertRows(['--skip-lines', '3', '-c', '1', '-m', '1', 'examples/test_skip_lines.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_match(self):
        self.assertRows(['-c', '1', '-m', '1', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_any_match(self):
        self.assertRows(['-c', '1,2,3', '-a', '-m', '1', 'examples/dummy.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_match_utf8(self):
        self.assertRows(['-c', '3', '-m', 'ʤ', 'examples/test_utf8.csv'], [
            ['foo', 'bar', 'baz'],
            ['4', '5', 'ʤ'],
        ])

    def test_match_utf8_bom(self):
        self.assertRows(['-c', '3', '-m', 'ʤ', 'examples/test_utf8_bom.csv'], [
            ['foo', 'bar', 'baz'],
            ['4', '5', 'ʤ'],
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

    def test_re_match_utf8(self):
        self.assertRows(['-c', '3', '-r', 'ʤ', 'examples/test_utf8.csv'], [
            ['foo', 'bar', 'baz'],
            ['4', '5', 'ʤ'],
        ])

    def assertMatchfileRows(self, text, rows, expected, extra_args=(), columns='1'):
        with TemporaryDirectory() as directory:
            matchfile = Path(directory) / 'matches.txt'
            matchfile.write_text(text, encoding='utf-8', newline='')
            input_file = Path(directory) / 'input.csv'
            with input_file.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream, quoting=csv.QUOTE_ALL)
                writer.writerows(rows)
            self.assertRows([
                '-c', columns, '-f', str(matchfile), *extra_args, str(input_file),
            ], expected)

    def test_file_match_preserves_whitespace(self):
        for value in ('value ', 'value\t', 'value\u00a0', 'value\u2003', ' \t'):
            for ending in ('\n', '\r\n', '\r', ''):
                with self.subTest(value=value, ending=ending):
                    self.assertMatchfileRows(value + ending, [
                        ['key', 'label'],
                        [value.rstrip(), 'trimmed'],
                        [value, 'exact'],
                        ['other', 'unrelated'],
                    ], [
                        ['key', 'label'],
                        [value, 'exact'],
                    ])

    def test_file_match_line_endings(self):
        for ending in ('\n', '\r\n', '\r', ''):
            with self.subTest(ending=ending):
                self.assertMatchfileRows('one' + ending, [
                    ['key'], ['one'], ['two'],
                ], [['key'], ['one']])

    def test_file_match_multiple_patterns(self):
        self.assertMatchfileRows('one \ntwo\t\r\nthree\u00a0', [
            ['key'], ['one'], ['one '], ['two'], ['two\t'], ['three'], ['three\u00a0'],
        ], [['key'], ['one '], ['two\t'], ['three\u00a0']])

    def test_file_match_inverted_whitespace(self):
        self.assertMatchfileRows('value \n', [
            ['key'], ['value'], ['value '], ['other'],
        ], [['key'], ['value'], ['other']], extra_args=('--invert-match',))

    def test_file_match_column_modes(self):
        rows = [
            ['first', 'second'], ['keep ', 'keep\t'], ['keep ', 'no'], ['no', 'keep\t'], ['keep', 'keep'],
        ]
        for extra_args, expected in (
            ((), [rows[0], rows[1]]),
            (('--any-match',), [rows[0], rows[1], rows[2], rows[3]]),
        ):
            with self.subTest(extra_args=extra_args):
                self.assertMatchfileRows('keep \nkeep\t\n', rows, expected, extra_args, '1,2')

    def test_string_match(self):
        self.assertRows(['-c', '1', '-m', 'ILLINOIS',
                         'examples/realdata/FY09_EDU_Recipients_by_State.csv'], [
            ['State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty',
                'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance',
                'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program',
                'TOTAL', ''],
            ['ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''],
        ])

    def test_match_with_line_numbers(self):
        self.assertRows(['-c', '1', '-m', 'ILLINOIS', '--linenumbers',
                         'examples/realdata/FY09_EDU_Recipients_by_State.csv'], [
            ['line_numbers', 'State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty',
                'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance',
                'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program',
                'TOTAL', ''],
            ['14', 'ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''],
        ])

    def test_kwargs_with_line_numbers(self):
        self.assertRows(['-t', '-c', '1', '-m', '1', '--linenumbers', 'examples/dummy.tsv'], [
            ['line_numbers', 'a', 'b', 'c'],
            ['1', '1', '2', '3'],
        ])
