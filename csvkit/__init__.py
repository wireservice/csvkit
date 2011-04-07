import argparse
import sys

def init_common_parser(description='',omitflags=''):
    """Prepare a base argparse argument parser so that flags are consistent across different shell command tools.
       If you want to constrain which common args are present, you can pass a string for 'omitflags'. Any argument
       whose single-letter form is contained in 'omitflags' will be left out of the configured parser.  Use 'f' for 
       file.
    """
    parser = argparse.ArgumentParser(description=description)
    if 'f' not in omitflags:
        parser.add_argument('file', metavar="FILE", nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
    if 'd' not in omitflags:
        parser.add_argument('-d', '--delimiter', dest='delimiter', default=',',
                            help='Delimiting character of the input CSV file. Defaults to comma.')
    if 't' not in omitflags:
        parser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                            help='Specifies that the input CSV file is delimited with tabs. Overrides "-d".')
    if 'q' not in omitflags:
        parser.add_argument('-q', '--quotechar', dest='quotechar', default='"',
                            help='Character used to quote strings in the input CSV file. Defaults to double-quote.')

    if 'e' not in omitflags:
        parser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                            help='NOT YET IMPLEMENTED. Reserving flag for unicode-aware future.')

    return parser                    