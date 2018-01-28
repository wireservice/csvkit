#!/usr/bin/env python

import os.path
import sys

import agate

from csvkit.cli import CSVKitUtility, make_default_headers


class CSVStack(CSVKitUtility):
    description = 'Stack up the rows from multiple CSV files, optionally adding a grouping value.'
    # Override 'f' because the utility accepts multiple files.
    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument(metavar='FILE', nargs='*', dest='input_paths', default=['-'],
                                    help='The CSV file(s) to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-g', '--groups', dest='groups',
                                    help='A comma-separated list of values to add as "grouping factors", one for each CSV being stacked. These will be added to the stacked CSV as a new column. You may specify a name for the grouping column using the -n flag.')
        self.argparser.add_argument('-n', '--group-name', dest='group_name',
                                    help='A name for the grouping column, e.g. "year". Only used when also specifying -g.')
        self.argparser.add_argument('--filenames', dest='group_by_filenames', action='store_true',
                                    help='Use the filename of each input file as its grouping value. When specified, -g will be ignored.')

    def main(self):
        if sys.stdin.isatty() and not self.args.input_paths:
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        has_groups = self.args.group_by_filenames or self.args.groups

        if self.args.groups and not self.args.group_by_filenames:
            groups = self.args.groups.split(',')

            if len(groups) != len(self.args.input_paths):
                self.argparser.error('The number of grouping values must be equal to the number of CSV files being stacked.')
        else:
            groups = None

        group_name = self.args.group_name if self.args.group_name else 'group'

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)

        for i, path in enumerate(self.args.input_paths):
            f = self._open_input_file(path)

            if isinstance(self.args.skip_lines, int):
                skip_lines = self.args.skip_lines
                while skip_lines > 0:
                    f.readline()
                    skip_lines -= 1
            else:
                raise ValueError('skip_lines argument must be an int')

            rows = agate.csv.reader(f, **self.reader_kwargs)

            if has_groups:
                if groups:
                    group = groups[i]
                else:
                    group = os.path.basename(f.name)

            # If we have header rows, use them
            if not self.args.no_header_row:
                headers = next(rows, [])

                if i == 0:
                    if has_groups:
                        headers.insert(0, group_name)

                    output.writerow(headers)
            # If we don't generate simple column names based on first row
            else:
                row = next(rows, [])

                headers = make_default_headers(len(row))

                if i == 0:
                    if has_groups:
                        headers.insert(0, group_name)

                    output.writerow(headers)

                if has_groups:
                    row.insert(0, group)

                output.writerow(row)

            for row in rows:
                if has_groups:
                    row.insert(0, group)

                output.writerow(row)

            f.close()


def launch_new_instance():
    utility = CSVStack()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
