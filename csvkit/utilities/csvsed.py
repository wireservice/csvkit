#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line interface to `csvsed.sed`.
"""

import agate
from csvkit.cli import CSVKitUtility
from sed import CSVModifier

class CSVSed(CSVKitUtility):

    description = 'A stream-oriented CSV modification tool. Like a ' \
                  ' stripped-down "sed" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to be modified.')
        self.argparser.add_argument('-m', '--modifier', dest='modifier',
                                    help='If specified, the "sed" modifier to evaluate: currently supports substitution '
                                      '(s/REGEX/REPL/FLAGS), transliteration (y/SRC/DEST/FLAGS) and execution '
                                      '(e/REGEX/COMMAND/FLAGS).')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if not self.args.columns:
            self.argparser.error('You must specify at least one column to search using the -c option.')

        if self.args.modifier is None:
            self.argparser.error('-m must be specified, unless using the -n option.')

        try:
          # decode if necessary, to work exclusively with unicode modifiers
          if isinstance(self.args.modifier, str):
              self.args.modifier = self.args.modifier.decode('utf-8')
        except AttributeError:
            # Ignore Python 3 error: 'str' object has no attribute 'decode'
            pass

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs
        if writer_kwargs.pop('line_numbers', False):
            reader_kwargs = {'line_numbers': True}

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)

        modifiers = {idx: self.args.modifier for idx in column_ids}
        reader = CSVModifier(rows, modifiers, header=False)

        output = agate.csv.writer(self.output_file, **writer_kwargs)
        output.writerow(column_names)

        for row in reader:
            output.writerow(row)

def launch_instance():
    utility = CSVSed()
    utility.main()

if __name__ == '__main__':
    launch_instance()