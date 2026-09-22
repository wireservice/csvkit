import io
import sys
from unittest.mock import patch

from agate import config

from csvkit.utilities.csvlook import CSVLook, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVLook(CSVKitTestCase, EmptyFileTests):
    Utility = CSVLook

    def tearDown(self):
        config.set_option('truncation_chars', '…')
        config.set_option('number_truncation_chars', '…')

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_encoding(self):
        self.assertLines(['-e', 'latin1', 'examples/test_latin1.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 4 | 5 | © |',
        ])

    def test_simple(self):
        self.assertLines(['examples/dummy3.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
            '| True | 4 | 5 |',
        ])

    def test_no_blanks(self):
        self.assertLines(['examples/blanks.csv'], [
            '| a | b | c | d | e | f |',
            '| - | - | - | - | - | - |',
            '|   |   |   |   |   |   |',
        ])

    def test_blanks(self):
        self.assertLines(['--blanks', 'examples/blanks.csv'], [
            '| a | b  | c   | d    | e    | f |',
            '| - | -- | --- | ---- | ---- | - |',
            '|   | NA | N/A | NONE | NULL | . |',
        ])

    def test_no_header_row(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 4 | 5 | 6 |',
        ])

    def test_unicode(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_unicode_bom(self):
        self.assertLines(['examples/test_utf8_bom.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy3.csv'], [
            '| line_numbers |    a | b | c |',
            '| ------------ | ---- | - | - |',
            '|            1 | True | 2 | 3 |',
            '|            2 | True | 4 | 5 |',
        ])

    def test_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 1 | 4 | 5 |',
        ])

    def test_sniff_limit_no_limit(self):
        self.assertLines(['examples/sniff_limit.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
        ])

    def test_sniff_limit_zero_limit(self):
        self.assertLines(['--snifflimit', '0', 'examples/sniff_limit.csv'], [
            '| a;b;c |',
            '| ----- |',
            '| 1;2;3 |',
        ])

    def test_max_rows(self):
        self.assertLines(['--max-rows', '0', 'examples/dummy.csv'], [
            '| a | b | c |',
            '| - | - | - |',
        ])

    def test_max_columns(self):
        self.assertLines(['--max-columns', '1', 'examples/dummy.csv'], [
            '|    a | ... |',
            '| ---- | --- |',
            '| True | ... |',
        ])

    def test_max_column_width(self):
        self.assertLines(['--max-column-width', '1', 'examples/dummy.csv'], [
            '|     a | b | c |',
            '| ----- | - | - |',
            '| Tr... | 2 | 3 |',
        ])

    def test_max_precision(self):
        self.assertLines(['--max-precision', '0', 'examples/test_precision.csv'], [
            '|  a |',
            '| -- |',
            '| 1… |',
        ])

    def test_no_number_ellipsis(self):
        self.assertLines(['--no-number-ellipsis', 'examples/test_precision.csv'], [
            '|     a |',
            '| ----- |',
            '| 1.235 |',
        ])

    def test_max_precision_no_number_ellipsis(self):
        self.assertLines(['--max-precision', '0', '--no-number-ellipsis', 'examples/test_precision.csv'], [
            '| a |',
            '| - |',
            '| 1 |',
        ])

    def test_stdin(self):
        input_file = io.BytesIO(b'a,b,c\n1,2,3\n4,5,6\n')

        with stdin_as_string(input_file):
            self.assertLines([], [
                '| a | b | c |',
                '| - | - | - |',
                '| 1 | 2 | 3 |',
                '| 4 | 5 | 6 |',
            ])

        input_file.close()

    def test_expanded(self):
        self.assertLines(['--expanded', 'examples/test_utf8.csv'], [
            '-[ RECORD 1 ]-',
            'foo | 1',
            'bar | 2',
            'baz | 3',
            '-[ RECORD 2 ]-',
            'foo | 4',
            'bar | 5',
            'baz | ʤ',
        ])

    def test_expanded_alignment_and_special_characters(self):
        data = 'name,notes,city\nOran,"first|second\nthird\tfourth",תל אביב\n'
        with stdin_as_string(io.BytesIO(data.encode('utf-8'))):
            self.assertLines(['--expanded', '-I', '-y', '0'], [
                '-[ RECORD 1 ]-',
                'name  | Oran',
                'notes | first|second↵third⇥fourth',
                'city  | תל אביב',
            ])

    def test_expanded_multiline_header(self):
        with stdin_as_string(io.BytesIO(b'"first\nname",age\nOran,35\n')):
            self.assertLines(['--expanded', '-I', '-y', '0'], [
                '-[ RECORD 1 ]-',
                'first↵name | Oran',
                'age        | 35',
            ])

    def test_expanded_no_inference(self):
        self.assertLines(['--expanded', '-I', 'examples/dummy.csv'], [
            '-[ RECORD 1 ]-', 'a | 1', 'b | 2', 'c | 3',
        ])

    def test_expanded_types_and_nulls(self):
        data = b'active,amount,date,missing\ntrue,1234.5,2026-09-08,\nfalse,2,2026-09-09,\n'
        with stdin_as_string(io.BytesIO(data)):
            self.assertLines(['--expanded', '-y', '0'], [
                '-[ RECORD 1 ]-',
                'active  | True', 'amount  | 1,234.5', 'date    | 2026-09-08', 'missing | ',
                '-[ RECORD 2 ]-',
                'active  | False', 'amount  | 2.0', 'date    | 2026-09-09', 'missing | ',
            ])

    def test_expanded_precision(self):
        for options, value in [
            ([], '1.235…'),
            (['--max-precision', '0'], '1…'),
            (['--no-number-ellipsis'], '1.235'),
            (['--max-precision', '0', '--no-number-ellipsis'], '1'),
        ]:
            with self.subTest(options=options):
                config.set_option('number_truncation_chars', '…')
                self.assertLines(['--expanded', '-y', '0', *options, 'examples/test_precision.csv'], [
                    '-[ RECORD 1 ]-', f'a | {value}',
                ])

    def test_expanded_infinite_numbers(self):
        with stdin_as_string(io.BytesIO(b'value\nInfinity\n-Infinity\n')):
            self.assertLines(['--expanded', '-y', '0'], [
                '-[ RECORD 1 ]-', 'value | Infinity', '-[ RECORD 2 ]-', 'value | -Infinity',
            ])

    def test_expanded_max_rows(self):
        self.assertLines(['--expanded', '--max-rows', '1', 'examples/dummy3.csv'], [
            '-[ RECORD 1 ]-', 'a | True', 'b | 2', 'c | 3',
        ])

    def test_expanded_zero_rows(self):
        self.assertEqual(self.get_output(['--expanded', '--max-rows', '0', 'examples/dummy.csv']), '')

    def test_expanded_max_columns(self):
        self.assertLines(['--expanded', '--max-columns', '1', 'examples/dummy.csv'], [
            '-[ RECORD 1 ]-', 'a   | True', '... | ...',
        ])

    def test_expanded_zero_columns(self):
        self.assertLines(['--expanded', '--max-columns', '0', 'examples/dummy.csv'], [
            '-[ RECORD 1 ]-', '... | ...',
        ])

    def test_expanded_max_column_width(self):
        with stdin_as_string(io.BytesIO(b'long_header,city\nlong_value,London\n')):
            self.assertLines(['--expanded', '-I', '--max-column-width', '6'], [
                '-[ RECORD 1 ]-', 'lon... | lon...', 'city   | London',
            ])

    def test_expanded_narrow_column_width(self):
        self.assertLines(['--expanded', '--max-column-width', '1', 'examples/dummy.csv'], [
            '-[ RECORD 1 ]-', 'a | ...', 'b | 2', 'c | 3',
        ])

    def test_expanded_empty_and_header_only(self):
        for data in [b'', b'name,city\n']:
            with self.subTest(data=data), stdin_as_string(io.BytesIO(data)):
                self.assertEqual(self.get_output(['--expanded', '-y', '0']), '')

    def test_expanded_line_numbers(self):
        self.assertLines(['--expanded', '--linenumbers', 'examples/dummy3.csv'], [
            '-[ RECORD 1 ]-', 'line_numbers | 1', 'a            | True', 'b            | 2', 'c            | 3',
            '-[ RECORD 2 ]-', 'line_numbers | 2', 'a            | True', 'b            | 4', 'c            | 5',
        ])

    def test_expanded_no_header_row(self):
        with stdin_as_string(io.BytesIO(b'Oran,London\n')):
            self.assertLines(['--expanded', '-I', '-H', '-y', '0'], [
                '-[ RECORD 1 ]-', 'a | Oran', 'b | London',
            ])

    def test_expanded_delimiter(self):
        with stdin_as_string(io.BytesIO(b'name;city\nOran;London\n')):
            self.assertLines(['--expanded', '-I', '-y', '0', '-d', ';'], [
                '-[ RECORD 1 ]-', 'name | Oran', 'city | London',
            ])
