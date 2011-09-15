#!/usr/bin/env python

import re
import sys
from argparse import FileType

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, CSVFileType, parse_column_identifiers, print_column_names
from csvkit.grep import FilteringCSVReader

class CSVGrep(CSVKitUtility):
    description = 'Search CSV files. Like the unix "grep" command, but for tabular data.'
    override_flags = 'f'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                        help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to be searched.')
        self.argparser.add_argument('-m','--match', dest="pattern", action='store',
                        help='The string to search for.')
        self.argparser.add_argument('-r', '--regex', dest='regex', action='store',
                        help='If specified, must be followed by a regular expression which will be tested against the specified columns.')
        self.argparser.add_argument('-f', '--file', dest='matchfile', type=FileType('r'), action='store',
                        help='If specified, must be the path to a file. For each tested row, if any line in the file (stripped of line separators) is an exact match for the cell value, the row will pass.')
        self.argparser.add_argument('-i', '--invert-match', dest='inverse', action='store_true',
                        help='If specified, select non-matching instead of matching rows.')
        self.argparser.add_argument('file', metavar="FILE", nargs='?', type=CSVFileType(), default=sys.stdin,
                        help='The CSV file to operate on. If omitted, will accept input on STDIN.')

    def main(self):
        if self.args.names_only:
            print_column_names(self.args.file, self.output_file, **self.reader_kwargs)
            return

        if not self.args.regex and not self.args.pattern and not self.args.matchfile:
            self.argparser.error("One of -r, -m or -f must be specified, unless using the -n option.")

        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = rows.next()

        column_ids = parse_column_identifiers(self.args.columns, column_names)
        
        if self.args.regex:
            pattern = re.compile(self.args.regex)
        elif self.args.matchfile:
            lines = [line.rstrip() for line in self.args.matchfile]
            pattern = lambda x: x in lines
        else:
            pattern = self.args.pattern
            
        patterns = dict((c, pattern) for c in column_ids)

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        output.writerow(column_names)

        filter_reader = FilteringCSVReader(rows, header=False, patterns=patterns, inverse=self.args.inverse)

        for i, row in enumerate(filter_reader):
            self.input_line_number = i + 1
            output.writerow(row)
                
if __name__ == "__main__":
    utility = CSVGrep()
    utility.main()

