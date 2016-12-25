#!/usr/bin/env python

"""
csvcut is originally the work of eminent hackers Joe Germuska and Aaron Bycoffe.

This code is forked from:
https://gist.github.com/561347/9846ebf8d0a69b06681da9255ffe3d3f59ec2c97

Used and modified with permission.
"""

import agate

from csvkit.cli import CSVKitUtility


class CSVCut(CSVKitUtility):
    description = 'Filter and truncate CSV files. Like the Unix "cut" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-C', '--not-columns', dest='not_columns',
                                    help='A comma separated list of column indices or names to be excluded. Defaults to no columns.')
        self.argparser.add_argument('-x', '--delete-empty-rows', dest='delete_empty', action='store_true',
                                    help='After cutting, delete rows which are completely empty.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**self.reader_kwargs)

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)
        output.writerow([column_names[column_id] for column_id in column_ids])

        for row in rows:
            out_row = [row[column_id] if column_id < len(row) else None for column_id in column_ids]

            if not self.args.delete_empty or ''.join(out_row):
                output.writerow(out_row)


def launch_new_instance():
    utility = CSVCut()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
