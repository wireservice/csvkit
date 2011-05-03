#!/usr/bin/env python

import argparse
import sys

from csvkit import CSVKitReader
from csvkit.exceptions import ColumnIdentifierError

class CSVKitUtility(object):
    description = ''
    epilog = ''
    override_flags = ''

    def __init__(self):
        """
        Perform argument processing and other setup for a CSVKitUtility.
        """
        self._init_common_parser()
        self.add_arguments()
        self.args = self.argparser.parse_args()

        self.reader_kwargs = self._extract_csv_reader_kwargs()
        self.writer_kwargs = self._extract_csv_writer_kwargs()

        self._install_exception_handler()

    def add_arguments(self):
        """
        Called upon initialization once the parser for common arguments has been constructed.

        Should be overriden by individual utilities.
        """
        raise NotImplementedError('add_arguments must be provided by each subclass of CSVKitUtility.')

    def main(self):
        """
        Main loop of the utility.

        Should be overriden by individual utilities and explicitly called by the executing script.
        """
        raise NotImplementedError(' must be provided by each subclass of CSVKitUtility.')

    def _init_common_parser(self):
        """
        Prepare a base argparse argument parser so that flags are consistent across different shell command tools.
        If you want to constrain which common args are present, you can pass a string for 'omitflags'. Any argument
        whose single-letter form is contained in 'omitflags' will be left out of the configured parser. Use 'f' for 
        file.
        """
        self.argparser = argparse.ArgumentParser(description=self.description, epilog=self.epilog)

        # Input
        if 'f' not in self.override_flags:
            self.argparser.add_argument('file', metavar="FILE", nargs='?', type=argparse.FileType('rU'), default=sys.stdin,
                                help='The CSV file to operate on. If omitted, will accept input on STDIN.')
        if 'd' not in self.override_flags:
            self.argparser.add_argument('-d', '--delimiter', dest='delimiter',
                                help='Delimiting character of the input CSV file.')
        if 't' not in self.override_flags:
            self.argparser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                                help='Specifies that the input CSV file is delimited with tabs. Overrides "-d".')
        if 'q' not in self.override_flags:
            self.argparser.add_argument('-q', '--quotechar', dest='quotechar',
                                help='Character used to quote strings in the input CSV file.')
        if 'u' not in self.override_flags:
            self.argparser.add_argument('-u', '--quoting', dest='quoting', type=int, choices=[0,1,2,3],
                                help='Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        if 'b' not in self.override_flags:
            self.argparser.add_argument('-b', '--doublequote', dest='doublequote', action='store_true',
                                help='Whether or not double quotes are doubled in the input CSV file.')
        if 'p' not in self.override_flags:
            self.argparser.add_argument('-p', '--escapechar', dest='escapechar',
                                help='Character used to escape the delimiter if quoting is set to "Quote None" and the quotechar if doublequote is not specified.')
        if 'e' not in self.override_flags:
            self.argparser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                                help='Specify the encoding the input file.')
        if 'v' not in self.override_flags:
            self.argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                help='Print detailed tracebacks when errors occur.')

        # Output
        if 'l' not in self.override_flags:
            self.argparser.add_argument('-l', '--linenumbers', dest='line_numbers', action='store_true',
                                help='Insert a column of line numbers at the front of the output. Useful when piping to grep or as a simple primary key.')

    def _extract_csv_reader_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
        """
        kwargs = {}
        if self.args.encoding:
            kwargs['encoding'] = self.args.encoding

        if self.args.tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.delimiter:
            kwargs['delimiter'] = self.args.delimiter

        if self.args.quotechar:
            kwargs['quotechar'] = self.args.quotechar

        if self.args.quoting:
            kwargs['quoting'] = self.args.quoting

        if self.args.doublequote:
            kwargs['doublequote'] = self.args.doublequote

        if self.args.escapechar:
            kwargs['escapechar'] = self.args.escapechar

        return kwargs

    def _extract_csv_writer_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the output CSV writer.
        """
        kwargs = {}

        if 'l' not in self.override_flags and self.args.line_numbers:
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
                print value

        sys.excepthook = handler

def match_column_identifier(column_names, c):
    """
    Determine what column a single column id (name or index) matches in a series of column names.
    """
    if c in column_names:
        return column_names.index(c)
    else:
        try:
            c = int(c) - 1
        # Fail out if neither a column name nor an integer
        except:
            raise ColumnIdentifierError('Column identifier "%s" is neither a index, nor a existing column\'s name.' % c)

        # Fail out if index is 0-based
        if c < 0:
            raise ColumnIdentifierError('Columns 0 is not valid; columns are 1-based.')

        # Fail out if index is out of range
        if c >= len(column_names):
            raise ColumnIdentifierError('Index %i is beyond the last named column, "%s" at index %i.' % (c, column_names[-1], len(column_names) - 1))

    return c

def parse_column_identifiers(ids, column_names):
    """
    Parse a comma-separated list of column indices AND/OR names into a list of integer indices.

    Note: Column indices are 1-based.
    """
    # If not specified, return all columns 
    if not ids:
        return range(len(column_names))

    columns = []

    for c in ids.split(','):
        columns.append(match_column_identifier(column_names, c.strip()))

    return columns

def print_column_names(f, output, **reader_kwargs):
    """
    Pretty-prints the names and indices of all columns to a file-like object (usually sys.stdout).
    """
    rows = CSVKitReader(f, **reader_kwargs)
    column_names = rows.next()

    for i, c in enumerate(column_names):
        output.write('%3i: %s\n' % (i + 1, c))

    sys.exit()
