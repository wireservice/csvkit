import bz2
import gzip
import io
import subprocess
import sys
import unittest
from unittest.mock import patch

from csvkit.cli import ColumnIdentifierError, match_column_identifier, parse_column_identifiers, zstandard
from csvkit.utilities.csvcut import CSVCut


class TestOutputCompression(unittest.TestCase):
    def run_cli(self, command, *args, data=b''):
        return subprocess.run([sys.executable, '-m', 'csvkit.utilities.' + command, *args],
                              input=data, capture_output=True)

    def test_round_trip(self):
        data = 'id,name\n1,"caf\u00e9\nau lait"\n'.encode()
        for command, args, stdin, status in (
            ('csvformat', ['--add-bom', '-T'], data, 0),
            ('csvlook', [], data, 0),
            ('csvstack', ['examples/dummy.csv.gz', 'examples/dummy.csv.bz2'], b'', 0),
            ('csvclean', ['--length-mismatch'], data + b'2\n', 1),
        ):
            plain = self.run_cli(command, *args, data=stdin)
            self.assertEqual(plain.returncode, status, plain.stderr)
            for codec, decompress, level in (('gzip', gzip.decompress, []),
                                             ('bz2', bz2.decompress, ['--compression-level', '1'])):
                with self.subTest(command=command, codec=codec):
                    result = self.run_cli(command, *args, '--output-compression', codec, *level, data=stdin)
                    self.assertEqual(result.returncode, status, result.stderr)
                    self.assertEqual(result.stderr, plain.stderr)
                    self.assertEqual(decompress(result.stdout), plain.stdout)
                    if codec == 'bz2':
                        self.assertTrue(result.stdout.startswith(b'BZh1'))

    def test_output_remains_open(self):
        with io.TextIOWrapper(io.BytesIO(), encoding='utf-8') as output:
            for codec in ('gzip', 'bz2'):
                utility = CSVCut(['--output-compression', codec, 'examples/dummy.csv'], output)
                utility.run()
                self.assertIs(utility.output_file, output)
                output.write('still open')

    @unittest.skipIf(zstandard is None, 'requires zstandard')
    def test_zstandard_output(self):
        data = 'id,name\n1,"caf\u00e9\nau lait"\n'.encode()
        plain = self.run_cli('csvcut', '--add-bom', data=data)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        for options in ([], ['--compression-level', '9']):
            with self.subTest(options=options):
                result = self.run_cli('csvcut', '--add-bom', '--output-compression', 'zst', *options, data=data)
                self.assertEqual(result.returncode, 0, result.stderr)
                decoder = zstandard.ZstdDecompressor().decompressobj()
                self.assertEqual(decoder.decompress(result.stdout), plain.stdout)
                self.assertTrue(decoder.eof)

    def test_zstandard_unavailable(self):
        with patch('csvkit.cli.zstandard', None), patch('sys.stderr', new_callable=io.StringIO) as stderr:
            with self.assertRaises(SystemExit) as error:
                CSVCut(['--output-compression', 'zst'])
            self.assertEqual(error.exception.code, 2)
            self.assertIn('requires the optional zstandard package', stderr.getvalue())

    def test_invalid_options(self):
        for command, args in (
            ('csvcut', ['--compression-level', '5']),
            ('csvcut', ['--output-compression', 'xz']),
            ('csvcut', ['--output-compression', 'gzip', '--compression-level', '0']),
            ('csvcut', ['--output-compression', 'bz2', '--compression-level', '10']),
            ('csvpy', ['--output-compression', 'gzip']),
        ):
            with self.subTest(command=command, args=args):
                result = self.run_cli(command, *args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b'')
                self.assertIn(b'error:', result.stderr)


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
