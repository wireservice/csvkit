#!/usr/bin/env python

"""
csvcut is originally the work of eminent hackers Joe Germuska and Aaron Bycoffe.

This code is forked from:
https://gist.github.com/561347/9846ebf8d0a69b06681da9255ffe3d3f59ec2c97

Used and modified with permission.
"""

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers, print_column_names

class CSVCut(CSVKitUtility):
    description = 'Filter and truncate CSV files. Like unix "cut" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                        help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-x', '--delete-empty-rows', dest='delete_empty', action='store_true',
                        help='After cutting, delete rows which are completely empty.')

    def main(self):
        if self.args.names_only:
            print_column_names(self.args.file, self.output_file, **self.reader_kwargs)
            return

        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = rows.next()

        column_ids = parse_column_identifiers(self.args.columns, column_names)
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)

        output.writerow([column_names[c] for c in column_ids])

        for i, row in enumerate(rows):
            self.input_line_number = i + 1
            out_row = [row[c] if c < len(row) else None for c in column_ids] 

            if self.args.delete_empty:
                if ''.join(out_row) == '':
                    continue
            
            output.writerow(out_row)
                
if __name__ == "__main__":
    utility = CSVCut()
    utility.main()

