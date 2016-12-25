#!/usr/bin/env python

import os

import agate

from csvkit.cli import CSVKitUtility, make_default_headers


class CSVStack(CSVKitUtility):
    description = 'Stack up the rows from multiple CSV files, optionally adding a grouping value.'
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument(metavar="FILE", nargs='+', dest='input_paths', default=['-'],
                                    help='The CSV file(s) to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-g', '--groups', dest='groups',
                                    help='A comma-separated list of values to add as "grouping factors", one for each CSV being stacked. These will be added to the stacked CSV as a new column. You may specify a name for the grouping column using the -n flag.')
        self.argparser.add_argument('-n', '--group-name', dest='group_name',
                                    help='A name for the grouping column, e.g. "year". Only used when also specifying -g.')
        self.argparser.add_argument('--filenames', dest='group_by_filenames', action='store_true',
                                    help='Use the filename of each input file as its grouping value. When specified, -g will be ignored.')

    def main(self):
        self.input_files = []

        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        if not self.input_files:
            self.argparser.error('You must specify at least one file to stack.')

        if self.args.group_by_filenames:
            groups = [os.path.split(f.name)[1] for f in self.input_files]
        elif self.args.groups:
            groups = self.args.groups.split(',')

            if len(groups) != len(self.input_files):
                self.argparser.error('The number of grouping values must be equal to the number of CSV files being stacked.')
        else:
            groups = None

        group_name = self.args.group_name if self.args.group_name else 'group'

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)

        for i, f in enumerate(self.input_files):
            rows = agate.csv.reader(f, **self.reader_kwargs)

            # If we have header rows, use them
            if not self.args.no_header_row:
                headers = next(rows, [])

                if i == 0:
                    if groups:
                        headers.insert(0, group_name)

                    output.writerow(headers)
            # If we don't generate simple column names based on first row
            else:
                row = next(rows, [])

                headers = make_default_headers(len(row))

                if i == 0:
                    if groups:
                        headers.insert(0, group_name)

                    output.writerow(headers)

                if groups:
                    row.insert(0, groups[i])

                output.writerow(row)

            for row in rows:
                if groups:
                    row.insert(0, groups[i])

                output.writerow(row)

            f.close()


def launch_new_instance():
    utility = CSVStack()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
