import argparse
import sys

def init_common_parser(description='', epilog='', omitflags=''):
    """Prepare a base argparse argument parser so that flags are consistent across different shell command tools.
       If you want to constrain which common args are present, you can pass a string for 'omitflags'. Any argument
       whose single-letter form is contained in 'omitflags' will be left out of the configured parser.  Use 'f' for 
       file.
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    if 'f' not in omitflags:
        parser.add_argument('file', metavar="FILE", nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
    if 'd' not in omitflags:
        parser.add_argument('-d', '--delimiter', dest='delimiter',
                            help='Delimiting character of the input CSV file. Defaults to comma.')
    if 't' not in omitflags:
        parser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                            help='Specifies that the input CSV file is delimited with tabs. Overrides "-d".')
    if 'q' not in omitflags:
        parser.add_argument('-q', '--quotechar', dest='quotechar',
                            help='Character used to quote strings in the input CSV file. Defaults to double-quote.')
    if 'u' not in omitflags:
        parser.add_argument('-u', '--quoting', dest='quoting', choices=[0,1,2,3],
                            help='Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
    if 'r' not in omitflags:
        parser.add_argument('-r', '--lineterminator', dest='lineterminator',
                            help='Character(s) used to terminate a line in the input CSV file.')
    if 'b' not in omitflags:
        parser.add_argument('-b', '--doublequote', dest='doublequote', action='store_true',
                            help='Whether or not double quotes are doubled in the input CSV file.')
    if 'p' not in omitflags:
        parser.add_argument('-p`', '--escapechar', dest='escapechar',
                            help='Character usedto escape the delimiter if quoting is set to "Quote None" and the quotechar if doublequote is not specified.')

    if 'e' not in omitflags:
        parser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                            help='Specify the encoding the input file.')


    return parser

def extract_csv_reader_kwargs(args):
    """
    Extracts those from the command-line arguments those would should be passed through to the CSV reader.
    """
    kwargs = {}
    if args.encoding:
        kwargs['encoding'] = args.encoding

    if args.delimiter:
        kwargs['delimiter'] = '\t' if args.tabs else args.delimiter

    if args.quotechar:
        kwargs['quotechar'] = args.quotechar

    if args.quotechar:
        kwargs['quoting'] = args.quoting

    if args.quotechar:
        kwargs['lineterminator'] = args.lineterminator

    if args.doublequote:
        kwargs['doublequote'] = args.doublequote

    if args.escapechar:
        kwargs['escapechar'] = args.escapechar

    return kwargs
