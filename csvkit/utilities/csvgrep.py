#!/usr/bin/env python

import re
from argparse import FileType

import agate

from csvkit.cli import CSVKitUtility
from csvkit.grep import FilteringCSVReader


class CSVGrep(CSVKitUtility):
    description = 'Search CSV files. Like the Unix "grep" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to be searched.')
        self.argparser.add_argument('-m', '--match', dest="pattern", action='store',
                                    help='The string to search for.')
        self.argparser.add_argument('-r', '--regex', dest='regex', action='store',
                                    help='If specified, must be followed by a regular expression which will be tested against the specified columns.')
        self.argparser.add_argument('-f', '--file', dest='matchfile', type=FileType('r'), action='store',
                                    help='If specified, must be the path to a file. For each tested row, if any line in the file (stripped of line separators) is an exact match for the cell value, the row will pass.')
        self.argparser.add_argument('-i', '--invert-match', dest='inverse', action='store_true',
                                    help='If specified, select non-matching instead of matching rows.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if not self.args.columns:
            self.argparser.error('You must specify at least one column to search using the -c option.')

        if self.args.regex is None and self.args.pattern is None and self.args.matchfile is None:
            self.argparser.error('One of -r, -m or -f must be specified, unless using the -n option.')

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs
        if writer_kwargs.pop('line_numbers', False):
            reader_kwargs = {'line_numbers': True}

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)

        if self.args.regex:
            pattern = re.compile(self.args.regex)
        elif self.args.matchfile:
            lines = set(line.rstrip() for line in self.args.matchfile)

            def pattern(x):
                return x in lines
        else:
            pattern = self.args.pattern

        patterns = dict((column_id, pattern) for column_id in column_ids)
        filter_reader = FilteringCSVReader(rows, header=False, patterns=patterns, inverse=self.args.inverse)

        output = agate.csv.writer(self.output_file, **writer_kwargs)
        output.writerow(column_names)

        for row in filter_reader:
            output.writerow(row)


def launch_new_instance():
    utility = CSVGrep()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
