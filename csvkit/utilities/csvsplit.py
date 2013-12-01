#!/usr/bin/env python

"""
csvsplit
"""

import itertools

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility
from csvkit.headers import make_default_headers

class CSVSplit(CSVKitUtility):
    description = ' Split CSV files by lines. Like unix "split" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--nlines', dest='lines', default=-1, type=int,
                        help='Number of lines to split the file.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to Use. Can rename existing columns.')

    def main(self):
        rows = CSVKitReader(self.args.file, **self.reader_kwargs)

        if self.args.no_header_row:
            row = rows.next()

            column_names = make_default_headers(len(row))

            # Put the row back on top
            rows = itertools.chain([row], rows)
        else:
            column_names = rows.next()

        column_names = self.args.columns.split(',')

        part_count = 0
        output = CSVKitWriter( open(self.args.file._lazy_args[0]+".part.%d" % part_count, 'w'), **self.writer_kwargs)
        output.writerow(column_names)

        count = 0
        for row in rows:
            if (self.args.lines > 0) and (count == self.args.lines):
                part_count += 1
                count = 0
                # couldn't find a better way to close the file
                del output
                output = CSVKitWriter( open(self.args.file._lazy_args[0]+".part.%d" % part_count, 'w'), **self.writer_kwargs)
                output.writerow(column_names)

            output.writerow(row)
            count += 1

                
def launch_new_instance():
    utility = CSVSplit()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

