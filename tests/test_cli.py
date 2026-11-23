import io
import os
import tempfile
import unittest
from codecs import BOM_UTF8
from unittest.mock import patch

from csvkit.cli import (ColumnIdentifierError, match_column_identifier, parse_column_identifiers,
                        reconfigure_output_stream)
from csvkit.utilities.csvclean import CSVClean
from csvkit.utilities.csvcut import CSVCut


def windows_stream():
    # A redirected standard stream, as on Windows: the locale encoding, and "\n" written as "\r\n".
    return io.TextIOWrapper(io.BytesIO(), encoding='cp1252', newline='\r\n', write_through=True)


class TestOutputStream(unittest.TestCase):

    def setUp(self):
        patcher = patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop('PYTHONIOENCODING', None)

    def test_writes_utf8_without_translating_newlines(self):
        stream = windows_stream()
        reconfigure_output_stream(stream)
        stream.write('a,"ʤ\nb"\n')
        self.assertEqual(stream.buffer.getvalue(), 'a,"ʤ\nb"\n'.encode())

    def test_keeps_pythonioencoding(self):
        os.environ['PYTHONIOENCODING'] = 'cp1252'
        stream = windows_stream()
        reconfigure_output_stream(stream)
        stream.write('é\n')
        self.assertEqual(stream.buffer.getvalue(), b'\xe9\n')

    def test_leaves_console_as_is(self):
        stream = windows_stream()
        with patch.object(stream, 'isatty', return_value=True):
            reconfigure_output_stream(stream)
        stream.write('é\n')
        self.assertEqual(stream.buffer.getvalue(), b'\xe9\r\n')

    def test_add_bom_writes_utf8(self):
        with patch('sys.stdout', windows_stream()) as stdout:
            CSVCut(['--add-bom', 'examples/test_utf8.csv']).run()
        self.assertEqual(stdout.buffer.getvalue(), BOM_UTF8 + 'foo,bar,baz\n1,2,3\n4,5,ʤ\n'.encode())

    def test_error_rows_write_utf8(self):
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write('a,b\n1,ʤ,extra\n')
        self.addCleanup(os.remove, f.name)
        with patch('sys.stdout', windows_stream()) as stdout, patch('sys.stderr', windows_stream()) as stderr:
            with self.assertRaises(SystemExit):
                CSVClean(['--length-mismatch', f.name]).run()
        self.assertEqual(stdout.buffer.getvalue(), 'a,b\n1,ʤ,extra\n'.encode())
        self.assertEqual(
            stderr.buffer.getvalue(),
            'line_number,msg,a,b\n1,"Expected 2 columns, found 3 columns",1,ʤ,extra\n'.encode(),
        )


class TestCli(unittest.TestCase):

    def setUp(self):
        self.headers = ['id', 'name', 'i_work_here', '1', 'more-header-values', 'stuff', 'blueberry']

    def test_match_column_identifier_string(self):
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here'))
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here', column_offset=0))

    def test_match_column_identifier_numeric(self):
        self.assertEqual(2, match_column_identifier(self.headers, 3))
        self.assertEqual(3, match_column_identifier(self.headers, 3, column_offset=0))

    def test_match_column_which_could_be_integer_name_is_treated_as_positional_id(self):
        self.assertEqual(0, match_column_identifier(self.headers, '1'))
        self.assertEqual(1, match_column_identifier(self.headers, '1', column_offset=0))

    def test_parse_column_identifiers(self):
        self.assertEqual([2, 0, 1], parse_column_identifiers('i_work_here,1,name', self.headers))
        self.assertEqual([2, 1, 1], parse_column_identifiers('i_work_here,1,name', self.headers, column_offset=0))
        self.assertEqual(
            [1, 1],
            parse_column_identifiers(
                'i_work_here,1,name',
                self.headers,
                column_offset=0,
                excluded_columns='i_work_here,foobar',
            ),
        )

    def test_range_notation(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers('1:3', self.headers))
        self.assertEqual([1, 2, 3], parse_column_identifiers('1:3', self.headers, column_offset=0))
        self.assertEqual([1, 2, 3], parse_column_identifiers('2-4', self.headers))
        self.assertEqual([2, 3, 4], parse_column_identifiers('2-4', self.headers, column_offset=0))
        self.assertEqual([0, 1, 2, 3], parse_column_identifiers('1,2:4', self.headers))
        self.assertEqual([1, 2, 3, 4], parse_column_identifiers('1,2:4', self.headers, column_offset=0))
        self.assertEqual([4, 2, 5], parse_column_identifiers('more-header-values,3,stuff', self.headers))
        self.assertEqual([4, 3, 5], parse_column_identifiers(
            'more-header-values,3,stuff', self.headers, column_offset=0))

    def test_ignore_unknown_columns(self):
        self.assertEqual(
            [0, 2],
            parse_column_identifiers('id,nope,i_work_here', self.headers, ignore_unknown_columns=True),
        )
        self.assertEqual(
            [],
            parse_column_identifiers('nope,missing', self.headers, ignore_unknown_columns=True),
        )
        # An unknown identifier containing '-' or ':' is skipped too, not parsed as a range.
        self.assertEqual(
            [0, 2],
            parse_column_identifiers('id,no-pe,i_work_here', self.headers, ignore_unknown_columns=True),
        )
        # Without the flag, the same input still raises.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers('id,no-pe,i_work_here', self.headers)

    def test_exclude_open_ended_range(self):
        # An open-ended exclusion range reaches the last column.
        self.assertEqual(
            [0, 1, 2, 3, 4],
            parse_column_identifiers(None, self.headers, excluded_columns='6-'),
        )

    def test_exclude_ignores_unknown_names_but_reports_invalid_ranges(self):
        # An unknown bare name is skipped (long-standing -C tolerance)...
        self.assertEqual(
            [0, 1, 2, 3, 4, 5, 6],
            parse_column_identifiers(None, self.headers, excluded_columns='nope'),
        )
        # ...but a malformed range is a user error, even for -C.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers(None, self.headers, excluded_columns='no-pe')
        # ...as is a range that references a nonexistent column.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers(None, self.headers, excluded_columns='6-99')

    def test_range_notation_open_ended(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers(':3', self.headers))

        target = list(range(3, len(self.headers)))  # protect against devs adding to self.headers
        target.insert(0, 0)
        self.assertEqual(target, parse_column_identifiers('1,4:', self.headers))

        target = list(range(0, len(self.headers)))
        self.assertEqual(target, parse_column_identifiers('1:', self.headers))

    def test_range_notation_open_ended_zero(self):
        self.assertEqual([0, 1, 2, 3], parse_column_identifiers(':3', self.headers, column_offset=0))

        target = list(range(4, len(self.headers)))  # protect against devs adding to self.headers
        target.insert(0, 1)
        self.assertEqual(target, parse_column_identifiers('1,4:', self.headers, column_offset=0))

        target = list(range(0, len(self.headers)))
        self.assertEqual(target, parse_column_identifiers('0:', self.headers, column_offset=0))
