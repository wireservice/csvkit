#!/usr/bin/env python
import argparse
import ast
import bz2
import csv
import datetime
import decimal
import gzip
import itertools
import lzma
import os
import re
import sys
import warnings
from codecs import BOM_UTF8
from glob import glob
from os.path import splitext

import agate
from agate.data_types.base import DEFAULT_NULL_VALUES

from csvkit.exceptions import ColumnIdentifierError, RequiredHeaderError

try:
    import zstandard
except ImportError:
    zstandard = None

QUOTING_CHOICES = sorted(getattr(csv, name) for name in dir(csv) if name.startswith('QUOTE_'))


class LazyFile:
    """
    A proxy for a File object that delays opening it until
    a read method is called.

    Currently this implements only the minimum methods to be useful,
    but it could easily be expanded.
    """

    def __init__(self, init, *args, **kwargs):
        self.init = init
        self.f = None
        self._is_lazy_opened = False

        self._lazy_args = args
        self._lazy_kwargs = kwargs

    def __getattr__(self, name):
        self._open()
        return getattr(self.f, name)

    def __iter__(self):
        return self

    def close(self):
        if self._is_lazy_opened:
            self.f.close()
            self.f = None
            self._is_lazy_opened = False

    def __next__(self):
        self._open()
        return next(self.f).replace('\0', '')

    def _open(self):
        if not self._is_lazy_opened:
            self.f = self.init(*self._lazy_args, **self._lazy_kwargs)
            self._is_lazy_opened = True


class CSVKitUtility:
    description = ''
    epilog = ''
    override_flags = ''

    def __init__(self, args=None, output_file=None, error_file=None):
        """
        Perform argument processing and other setup for a CSVKitUtility.
        """
        if args is None:
            args = sys.argv[1:]
        if os.name == 'nt':
            args = _expand_args(args)

        self._init_common_parser()
        self.add_arguments()
        self.args = self.argparser.parse_args(args)

        # Output file is only set during testing.
        if output_file is None:
            self.output_file = sys.stdout
        else:
            self.output_file = output_file

        # Error file is only set during testing.
        if error_file is None:
            self.error_file = sys.stderr
        else:
            self.error_file = error_file

        self.reader_kwargs = self._extract_csv_reader_kwargs()
        self.writer_kwargs = self._extract_csv_writer_kwargs()

        self._install_exception_handler()

        # Ensure SIGPIPE doesn't throw an exception
        # Prevents [Errno 32] Broken pipe errors, e.g. when piping to 'head'
        # To test from the shell:
        #  python -c "for i in range(5000): print('a,b,c')" | csvlook | head
        # Without this fix you will see at the end:
        #  [Errno 32] Broken pipe
        # With this fix, there should be no error
        # For details on Python and SIGPIPE, see https://bugs.python.org/issue1652
        try:
            import signal
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        except (ImportError, AttributeError):
            # Do nothing on platforms that don't have signals or don't have SIGPIPE
            pass

    def add_arguments(self):
        """
        Called upon initialization once the parser for common arguments has been constructed.

        Should be overridden by individual utilities.
        """
        raise NotImplementedError('add_arguments must be provided by each subclass of CSVKitUtility.')

    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.
        """
        if 'f' not in self.override_flags:
            self.input_file = self._open_input_file(self.args.input_path)

        if getattr(self.args, 'add_bom', False):
            self.output_file.buffer.write(BOM_UTF8)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, 'no_header_row', None):
                    warnings.filterwarnings(action='ignore', message='Column names not specified', module='agate')

                self.main()
        finally:
            if 'f' not in self.override_flags:
                self.input_file.close()

    def main(self):
        """
        Main loop of the utility.

        Should be overridden by individual utilities and explicitly called by the executing script.
        """
        raise NotImplementedError(' must be provided by each subclass of CSVKitUtility.')

    def _init_common_parser(self):
        """
        Prepare a base argparse argument parser so that flags are consistent across different shell command tools.
        If you want to constrain which common args are present, you can pass a string for 'omitflags'. Any argument
        whose single-letter form is contained in 'omitflags' will be left out of the configured parser. Use 'f' for
        file.
        """
        self.argparser = argparse.ArgumentParser(
            prog=type(self).__name__.lower(), description=self.description, epilog=self.epilog
        )

        # Input
        if 'f' not in self.override_flags:
            self.argparser.add_argument(
                metavar='FILE', nargs='?', dest='input_path',
                help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')
        if 'd' not in self.override_flags:
            self.argparser.add_argument(
                '-d', '--delimiter', dest='delimiter',
                help='Delimiting character of the input CSV file.')
        if 't' not in self.override_flags:
            self.argparser.add_argument(
                '-t', '--tabs', dest='tabs', action='store_true',
                help='Specify that the input CSV file is delimited with tabs. Overrides "-d".')
        if 'q' not in self.override_flags:
            self.argparser.add_argument(
                '-q', '--quotechar', dest='quotechar',
                help='Character used to quote strings in the input CSV file.')
        if 'u' not in self.override_flags:
            self.argparser.add_argument(
                '-u', '--quoting', dest='quoting', type=int, choices=QUOTING_CHOICES,
                help='Quoting style used in the input CSV file: 0 quote minimal, 1 quote all, '
                     '2 quote non-numeric, 3 quote none.')
        if 'b' not in self.override_flags:
            self.argparser.add_argument(
                '-b', '--no-doublequote', dest='doublequote', action='store_false',
                help='Whether or not double quotes are doubled in the input CSV file.')
        if 'p' not in self.override_flags:
            self.argparser.add_argument(
                '-p', '--escapechar', dest='escapechar',
                help='Character used to escape the delimiter if --quoting 3 ("quote none") is specified and to escape '
                     'the QUOTECHAR if --no-doublequote is specified.')
        if 'z' not in self.override_flags:
            self.argparser.add_argument(
                '-z', '--maxfieldsize', dest='field_size_limit', type=int,
                help='Maximum length of a single field in the input CSV file.')
        if 'e' not in self.override_flags:
            self.argparser.add_argument(
                '-e', '--encoding', dest='encoding', default=os.getenv('PYTHONIOENCODING', 'utf-8-sig'),
                help='Specify the encoding of the input CSV file.')
        if 'L' not in self.override_flags:
            self.argparser.add_argument(
                '-L', '--locale', dest='locale', default='en_US',
                help='Specify the locale (en_US) of any formatted numbers.')
        if 'S' not in self.override_flags:
            self.argparser.add_argument(
                '-S', '--skipinitialspace', dest='skipinitialspace', action='store_true',
                help='Ignore whitespace immediately following the delimiter.')
        if 'I' not in self.override_flags:
            self.argparser.add_argument(
                '--blanks', dest='blanks', action='store_true',
                help='Do not convert "", "na", "n/a", "none", "null", "." to NULL.')
            self.argparser.add_argument(
                '--null-value', dest='null_values', nargs='+', default=[],
                help='Convert this value to NULL. --null-value can be specified multiple times.')
            self.argparser.add_argument(
                '--date-format', dest='date_format',
                help='Specify a strptime date format string like "%%m/%%d/%%Y".')
            self.argparser.add_argument(
                '--datetime-format', dest='datetime_format',
                help='Specify a strptime datetime format string like "%%m/%%d/%%Y %%I:%%M %%p".')
            self.argparser.add_argument(
                '--no-leading-zeroes', dest='no_leading_zeroes', action='store_true',
                help='Do not convert a numeric value with leading zeroes to a number.')
        if 'H' not in self.override_flags:
            self.argparser.add_argument(
                '-H', '--no-header-row', dest='no_header_row', action='store_true',
                help='Specify that the input CSV file has no header row. Will create default headers (a,b,c,...).')
        if 'K' not in self.override_flags:
            self.argparser.add_argument(
                '-K', '--skip-lines', dest='skip_lines', type=int, default=0,
                help='Specify the number of initial lines to skip before the header row (e.g. comments, copyright '
                     'notices, empty rows).')
        if 'v' not in self.override_flags:
            self.argparser.add_argument(
                '-v', '--verbose', dest='verbose', action='store_true',
                help='Print detailed tracebacks when errors occur.')

        # Output
        if 'l' not in self.override_flags:
            self.argparser.add_argument(
                '-l', '--linenumbers', dest='line_numbers', action='store_true',
                help='Insert a column of line numbers at the front of the output. Useful when piping to grep or as a '
                     'simple primary key.')
        if 'add-bom' not in self.override_flags:
            self.argparser.add_argument(
                '--add-bom', dest='add_bom', action='store_true',
                help='Add the UTF-8 byte-order mark (BOM) to the output, for Excel compatibility')

        # Input/Output
        if 'zero' not in self.override_flags:
            self.argparser.add_argument(
                '--zero', dest='zero_based', action='store_true',
                help='When interpreting or displaying column numbers, use zero-based numbering instead of the default '
                     '1-based numbering.')

        self.argparser.add_argument(
            '-V', '--version', action='version', version='%(prog)s 2.1.0',
            help='Display version information and exit.')

    def _open_input_file(self, path, opened=False):
        """
        Open the input file specified on the command line.
        """
        if not path or path == '-':
            # "UnsupportedOperation: It is not possible to set the encoding or newline of stream after the first read"
            if not opened:
                sys.stdin.reconfigure(encoding=self.args.encoding)
            f = sys.stdin
        else:
            extension = splitext(path)[1]

            if extension == '.gz':
                func = gzip.open
            elif extension == '.bz2':
                func = bz2.open
            elif extension == '.xz':
                func = lzma.open
            elif extension == '.zst' and zstandard:
                func = zstandard.open
            else:
                func = open

            f = LazyFile(func, path, mode='rt', encoding=self.args.encoding)

        return f

    def _extract_csv_reader_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
        """
        kwargs = {}

        field_size_limit = getattr(self.args, 'field_size_limit')
        if field_size_limit is not None:
            csv.field_size_limit(field_size_limit)

        if self.args.tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.delimiter:
            kwargs['delimiter'] = self.args.delimiter

        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'skipinitialspace'):
            value = getattr(self.args, arg)
            if value is not None:
                kwargs[arg] = value

        if getattr(self.args, 'no_header_row', None):
            kwargs['header'] = not self.args.no_header_row

        return kwargs

    def _extract_csv_writer_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the output CSV writer.
        """
        kwargs = {}

        if getattr(self.args, 'line_numbers', None):
            kwargs['line_numbers'] = True

        return kwargs

    def _install_exception_handler(self):
        """
        Installs a replacement for sys.excepthook, which handles pretty-printing uncaught exceptions.
        """
        def handler(t, value, traceback):
            if self.args.verbose:
                sys.__excepthook__(t, value, traceback)
            else:
                # Special case handling for Unicode errors, which behave very strangely
                # when cast with unicode()
                if t == UnicodeDecodeError:
                    sys.stderr.write(
                        'Your file is not "%s" encoded. Please specify the correct encoding with the --encoding flag.'
                        ' Use the -v flag to see the complete error.\n' % self.args.encoding
                    )
                else:
                    sys.stderr.write(f'{t.__name__}: {str(value)}\n')

        sys.excepthook = handler

    def get_column_types(self):
        if getattr(self.args, 'blanks', None):
            type_kwargs = {'null_values': []}
        else:
            type_kwargs = {'null_values': list(DEFAULT_NULL_VALUES)}
        for null_value in getattr(self.args, 'null_values', []):
            type_kwargs['null_values'].append(null_value)

        text_type = agate.Text(**type_kwargs)

        if getattr(self.args, 'no_inference', None):
            types = [text_type]
        else:
            number_type = agate.Number(
                locale=self.args.locale, no_leading_zeroes=getattr(self.args, 'no_leading_zeroes', None), **type_kwargs
            )

            if getattr(self.args, 'out_quoting', None) == 2:  # QUOTE_NONUMERIC
                types = [number_type, text_type]
            else:
                # See the order in the `agate.TypeTester` class.
                types = [
                    agate.Boolean(**type_kwargs),
                    agate.TimeDelta(**type_kwargs),
                    agate.Date(date_format=self.args.date_format, **type_kwargs),
                    agate.DateTime(datetime_format=self.args.datetime_format, **type_kwargs),
                    text_type,
                ]

                # In order to parse dates like "20010101".
                if self.args.datetime_format:
                    types.insert(-1, number_type)
                elif self.args.date_format:
                    types.insert(-2, number_type)
                else:
                    types.insert(1, number_type)

        return agate.TypeTester(types=types)

    def get_column_offset(self):
        if self.args.zero_based:
            return 0
        return 1

    def skip_lines(self):
        if isinstance(self.args.skip_lines, int):
            while self.args.skip_lines > 0:
                self.input_file.readline()
                self.args.skip_lines -= 1
        else:
            raise ValueError('skip_lines argument must be an int')

        return self.input_file

    def get_rows_and_column_names_and_column_ids(self, **kwargs):
        rows = agate.csv.reader(self.skip_lines(), **kwargs)

        try:
            next_row = next(rows)
        except StopIteration:
            return iter([]), [], []

        if self.args.no_header_row:
            # Peek at a row to get the number of columns.
            row = next_row
            rows = itertools.chain([row], rows)
            column_names = make_default_headers(len(row))
        else:
            column_names = next_row

        column_offset = self.get_column_offset()
        if kwargs.get('line_numbers'):
            column_offset -= 1

        column_ids = parse_column_identifiers(
            self.args.columns,
            column_names,
            column_offset,
            getattr(self.args, 'not_columns', None),
        )

        return rows, column_names, column_ids

    def print_column_names(self):
        """
        Pretty-prints the names and indices of all columns to a file-like object (usually sys.stdout).
        """
        if getattr(self.args, 'no_header_row', None):
            raise RequiredHeaderError('You cannot use --no-header-row with the -n or --names options.')

        if getattr(self.args, 'zero_based', None):
            start = 0
        else:
            start = 1

        rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        column_names = next(rows)

        for i, c in enumerate(column_names, start):
            self.output_file.write('%3i: %s\n' % (i, c))

    def additional_input_expected(self):
        return isatty(sys.stdin) and not self.args.input_path


def isatty(f):
    try:
        return f.isatty()
    except ValueError:  # I/O operation on closed file
        return False


def default_str_decimal(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError(f'{repr(obj)} is not JSON serializable')


def default_float_decimal(obj):
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return default_str_decimal(obj)


def make_default_headers(n):
    """
    Make a set of simple, default headers for files that are missing them.
    """
    return tuple(agate.utils.letter_name(i) for i in range(n))


def match_column_identifier(column_names, c, column_offset=1):
    """
    Determine what column a single column id (name or index) matches in a series of column names.
    Note that integer values are *always* treated as positional identifiers. If you happen to have
    column names which are also integers, you must specify them using a positional index.
    """
    if isinstance(c, str) and not c.isdigit() and c in column_names:
        return column_names.index(c)

    try:
        c = int(c) - column_offset
    # Fail out if neither a column name nor an integer
    except ValueError:
        raise ColumnIdentifierError("Column '%s' is invalid. It is neither an integer nor a column name. "
                                    "Column names are: %s" % (c, repr(column_names)[1:-1]))

    # Fail out if index is 0-based
    if c < 0:
        raise ColumnIdentifierError("Column %i is invalid. Columns are 1-based." % (c + column_offset))

    # Fail out if index is out of range
    if c >= len(column_names):
        raise ColumnIdentifierError("Column %i is invalid. The last column is '%s' at index %i." % (
            c + column_offset, column_names[-1], len(column_names) - 1 + column_offset))

    return c


def parse_column_identifiers(ids, column_names, column_offset=1, excluded_columns=None):
    """
    Parse a comma-separated list of column indices AND/OR names into a list of integer indices.
    Ranges of integers can be specified with two integers separated by a '-' or ':' character.
    Ranges of non-integers (e.g. column names) are not supported.
    Note: Column indices are 1-based.
    """
    if not column_names:
        return []

    if not ids and not excluded_columns:
        return range(len(column_names))

    if ids:
        columns = []

        for c in ids.split(','):
            try:
                columns.append(match_column_identifier(column_names, c, column_offset))
            except ColumnIdentifierError:
                if ':' in c:
                    a, b = c.split(':', 1)
                elif '-' in c:
                    a, b = c.split('-', 1)
                else:
                    raise

                try:
                    a = int(a) if a else 1
                    b = int(b) + 1 if b else len(column_names) + 1
                except ValueError:
                    raise ColumnIdentifierError(
                        "Invalid range %s. Ranges must be two integers separated by a - or : character.")

                for x in range(a, b):
                    columns.append(match_column_identifier(column_names, x, column_offset))
    else:
        columns = range(len(column_names))

    excludes = []

    if excluded_columns:
        for c in excluded_columns.split(','):
            try:
                excludes.append(match_column_identifier(column_names, c, column_offset))
            except ColumnIdentifierError:
                if ':' in c:
                    a, b = c.split(':', 1)
                elif '-' in c:
                    a, b = c.split('-', 1)
                else:
                    # Ignore unknown columns.
                    continue

                try:
                    a = int(a) if a else 1
                    b = int(b) + 1 if b else len(column_names)
                except ValueError:
                    raise ColumnIdentifierError(
                        "Invalid range %s. Ranges must be two integers separated by a - or : character.")

                for x in range(a, b):
                    excludes.append(match_column_identifier(column_names, x, column_offset))

    return [c for c in columns if c not in excludes]


def parse_list(pairs):
    options = {}
    for key, value in pairs:
        try:
            value = ast.literal_eval(value)
        except ValueError:
            pass
        options[key] = value
    return options


# Adapted from https://github.com/pallets/click/blame/main/src/click/utils.py
def _expand_args(args):
    out = []

    for arg in args:
        arg = os.path.expanduser(arg)
        arg = os.path.expandvars(arg)

        try:
            matches = glob(arg, recursive=True)
        except re.error:
            matches = []

        if matches:
            out.extend(matches)
        else:
            out.append(arg)

    return out
