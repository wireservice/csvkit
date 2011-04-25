#!/usr/bin/env python

import argparse
import sys

from csvkit.exceptions import ColumnIdentifierError

def init_common_parser(description='', epilog='', omitflags=''):
    """Prepare a base argparse argument parser so that flags are consistent across different shell command tools.
       If you want to constrain which common args are present, you can pass a string for 'omitflags'. Any argument
       whose single-letter form is contained in 'omitflags' will be left out of the configured parser.  Use 'f' for 
       file.
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    # Input
    if 'f' not in omitflags:
        parser.add_argument('file', metavar="FILE", nargs='?', type=argparse.FileType('rU'), default=sys.stdin,
                            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
    if 'd' not in omitflags:
        parser.add_argument('-d', '--delimiter', dest='delimiter',
                            help='Delimiting character of the input CSV file.')
    if 't' not in omitflags:
        parser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                            help='Specifies that the input CSV file is delimited with tabs. Overrides "-d".')
    if 'q' not in omitflags:
        parser.add_argument('-q', '--quotechar', dest='quotechar',
                            help='Character used to quote strings in the input CSV file.')
    if 'u' not in omitflags:
        parser.add_argument('-u', '--quoting', dest='quoting', type=int, choices=[0,1,2,3],
                            help='Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
    if 'b' not in omitflags:
        parser.add_argument('-b', '--doublequote', dest='doublequote', action='store_true',
                            help='Whether or not double quotes are doubled in the input CSV file.')
    if 'p' not in omitflags:
        parser.add_argument('-p', '--escapechar', dest='escapechar',
                            help='Character used to escape the delimiter if quoting is set to "Quote None" and the quotechar if doublequote is not specified.')
    if 'e' not in omitflags:
        parser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                            help='Specify the encoding the input file.')

    # Output
    if 'l' not in omitflags:
        parser.add_argument('-l', '--linenumbers', dest='line_numbers', action='store_true',
                            help='Insert a column of line numbers at the front of the output. Useful when piping to grep or as a simple primary key.')

    return parser

def extract_csv_reader_kwargs(args):
    """
    Extracts those from the command-line arguments those would should be passed through to the CSV reader.
    """
    kwargs = {}
    if args.encoding:
        kwargs['encoding'] = args.encoding

    if args.tabs:
        kwargs['delimiter'] = '\t'
    elif args.delimiter:
        kwargs['delimiter'] = args.delimiter

    if args.quotechar:
        kwargs['quotechar'] = args.quotechar

    if args.quotechar:
        kwargs['quoting'] = args.quoting

    if args.doublequote:
        kwargs['doublequote'] = args.doublequote

    if args.escapechar:
        kwargs['escapechar'] = args.escapechar

    return kwargs

def extract_csv_writer_kwargs(args):
    kwargs = {}

    if args.line_numbers:
        kwargs['line_numbers'] = True

    return kwargs

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
        columns.append(match_column_identifier(column_names, c))

    return columns

