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

    def test_describe(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2\n')):
            self.assertLines(['--describe'], [
                "Delimiter: ';'",
                'Quote character: \'"\'',
                'Escape character: None',
                'Double quote: True',
                'Quoting: 0',
                'Skip initial space: False',
            ])

    def test_describe_input_overrides(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2\n')):
            output = self.get_output(['--describe', '-t', '-d', '|', '-q', "'", '-p', '\\', '-u', '3', '-S'])
        self.assertIn("Delimiter: '\\t'\n", output)
        self.assertIn('Quote character: "\'"\n', output)
        self.assertIn("Escape character: '\\\\'\n", output)
        self.assertIn('Quoting: 3\n', output)
        self.assertIn('Skip initial space: True\n', output)

    def test_describe_skip_lines(self):
        with stdin_as_string(io.BytesIO(b'comment\ncomment\na;b\n1;2\n')):
            self.assertIn("Delimiter: ';'\n", self.get_output(['--describe', '-K', '2']))

    def test_describe_without_sniffing(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2\n')):
            self.assertIn("Delimiter: ','\n", self.get_output(['--describe', '-y', '0']))

    def test_describe_missing_file_without_sniffing(self):
        with self.assertRaises(FileNotFoundError):
            self.get_output(['--describe', '-y', '0', 'examples/missing-describe.csv'])

    def test_describe_sniff_limit(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2\n3,4\n')):
            self.assertIn("Delimiter: ';'\n", self.get_output(['--describe', '-y', '8']))

    def test_describe_entire_file(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2\n3,4\n')), self.assertWarns(RuntimeWarning):
            self.assertIn("Delimiter: ','\n", self.get_output(['--describe', '-y', '-1']))

    def test_describe_invalid_sniff_limit(self):
        self.assertError(launch_new_instance, ['--describe', '-y', '-2'], '--snifflimit must be -1 or greater.')

    def test_describe_empty(self):
        with self.assertWarns(RuntimeWarning):
            self.assertIn("Delimiter: ','\n", self.get_output(['--describe', 'examples/empty.csv']))

    def test_describe_without_parsing_rows(self):
        with stdin_as_string(io.BytesIO(b'a;b\n1;2;3\n')):
            self.assertIn("Delimiter: ';'\n", self.get_output(['--describe', '-y', '4', '-U', '2']))

    def test_describe_ignores_output_format(self):
        output = self.get_output(['--describe', '-D', '|', '-Q', '#', '-U', '2', 'examples/dummy.csv'])
        self.assertIn("Delimiter: ','\n", output)
        self.assertIn('Quote character: \'"\'\n', output)

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
