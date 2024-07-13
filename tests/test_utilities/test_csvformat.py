import io
import sys
from unittest.mock import patch

from csvkit.utilities.csvformat import CSVFormat, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVFormat(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFormat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertLines(['--skip-lines', '3', '-D', '|', 'examples/test_skip_lines.csv'], [
            'a|b|c',
            '1|2|3',
        ])

    def test_skip_header(self):
        self.assertLines(['--skip-header', 'examples/dummy.csv'], [
            '1,2,3',
        ])

    def test_skip_header_no_header_row(self):
        self.assertLines(['--no-header-row', '--skip-header', 'examples/no_header_row.csv'], [
            '1,2,3',
        ])

    def test_no_header_row(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row.csv'], [
            'a,b,c',
            '1,2,3',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy.csv'], [
            'line_number,a,b,c',
            '1,1,2,3',
        ])

    def test_delimiter(self):
        self.assertLines(['-D', '|', 'examples/dummy.csv'], [
            'a|b|c',
            '1|2|3',
        ])

    def test_tabs(self):
        self.assertLines(['-T', 'examples/dummy.csv'], [
            'a\tb\tc',
            '1\t2\t3',
        ])

    def test_asv(self):
        self.assertLines(['-A', 'examples/dummy.csv'], [
            'a\x1fb\x1fc\x1e1\x1f2\x1f3\x1e',
        ], newline_at_eof=False)

    def test_quotechar(self):
        input_file = io.BytesIO(b'a,b,c\n1#2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-Q', '#'], [
                'a,b,c',
                '#1##2#,3,4',
            ])

        input_file.close()

    def test_doublequote(self):
        input_file = io.BytesIO(b'a\n"a ""quoted"" string"')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-B'], [
                'a',
                'a #"quoted#" string',
            ])

        input_file.close()

    def test_escapechar(self):
        input_file = io.BytesIO(b'a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-U', '3'], [
                'a,b,c',
                '1#"2,3,4',
            ])

        input_file.close()

    def test_lineterminator(self):
        self.assertLines(['-M', 'XYZ', 'examples/dummy.csv'], [
            'a,b,cXYZ1,2,3XYZ',
        ], newline_at_eof=False)


class TestCSVFormatQuoteNonNumeric(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFormat

    # New test compared to TestCSVFormat.
    def test_locale(self):
        self.assertLines(['-U', '2', '--locale', 'de_DE', 'examples/test_locale.csv'], [
            '"a","b","c"',
            '1.7,200000000,""',
        ])

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertLines(['-U', '2', '--skip-lines', '3', '-D', '|', 'examples/test_skip_lines.csv'], [
            '"a"|"b"|"c"',
            '1|2|3',
        ])

    def test_skip_header(self):
        self.assertLines(['-U', '2', '--skip-header', 'examples/dummy.csv'], [
            '1,2,3',
        ])

    def test_skip_header_no_header_row(self):
        self.assertLines(['-U', '2', '--no-header-row', '--skip-header', 'examples/no_header_row.csv'], [
            '1,2,3',
        ])

    def test_no_header_row(self):
        self.assertLines(['-U', '2', '--no-header-row', 'examples/no_header_row.csv'], [
            '"a","b","c"',
            '1,2,3',
        ])

    def test_linenumbers(self):
        self.assertLines(['-U', '2', '--linenumbers', 'examples/dummy.csv'], [
            '"line_number","a","b","c"',
            '1,1,2,3',
        ])

    def test_delimiter(self):
        self.assertLines(['-U', '2', '-D', '|', 'examples/dummy.csv'], [
            '"a"|"b"|"c"',
            '1|2|3',
        ])

    def test_tabs(self):
        self.assertLines(['-U', '2', '-T', 'examples/dummy.csv'], [
            '"a"\t"b"\t"c"',
            '1\t2\t3',
        ])

    def test_asv(self):
        self.assertLines(['-U', '2', '-A', 'examples/dummy.csv'], [
            '"a"\x1f"b"\x1f"c"\x1e1\x1f2\x1f3\x1e',
        ], newline_at_eof=False)

    def test_quotechar(self):
        input_file = io.BytesIO(b'a,b,c\n1#2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-U', '2', '-Q', '#'], [
                '#a#,#b#,#c#',
                '#1##2#,3,4',
            ])

        input_file.close()

    def test_doublequote(self):
        input_file = io.BytesIO(b'a\n"a ""quoted"" string"')

        with stdin_as_string(input_file):
            self.assertLines(['-U', '2', '-P', '#', '-B'], [
                '"a"',
                '"a #"quoted#" string"',
            ])

        input_file.close()

    def test_escapechar(self):
        input_file = io.BytesIO(b'a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-U', '2', '-P', '#', '-U', '3'], [
                'a,b,c',
                '1#"2,3,4',
            ])

        input_file.close()

    def test_lineterminator(self):
        self.assertLines(['-U', '2', '-M', 'XYZ', 'examples/dummy.csv'], [
            '"a","b","c"XYZ1,2,3XYZ',
        ], newline_at_eof=False)
