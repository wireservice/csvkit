#!/usr/bin/env python

import os

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVFileType, CSVKitUtility

class CSVStack(CSVKitUtility):
    description = 'Stack up the rows from multiple CSV files, optionally adding a grouping value.'
    override_flags = 'f'

    def add_arguments(self):
        self.argparser.add_argument('files', metavar='FILES', nargs='+', type=CSVFileType())
        self.argparser.add_argument('-g', '--groups', dest='groups',
                            help='A comma-seperated list of values to add as "grouping factors", one for each CSV being stacked. These will be added to the stacked CSV as a new column. You may specify a name for the grouping column using the -n flag.')
        self.argparser.add_argument('-n', '--group-name', dest='group_name',
                            help='A name for the grouping column, e.g. "year". Only used when also specifying -g.')
        self.argparser.add_argument('--filenames', dest='group_by_filenames', action='store_true',
                            help='Use the filename of each input file as its grouping value. When specified, -g will be ignored.')

    def main(self):
        if len(self.args.files) < 2:
            self.argparser.error('You must specify at least two files to stack.')

        if self.args.group_by_filenames:
            groups = [os.path.split(f.name)[1] for f in self.args.files] 
        elif self.args.groups:
            groups = self.args.groups.split(',')

            if len(groups) != len(self.args.files):
                self.argparser.error('The number of grouping values must be equal to the number of CSV files being stacked.')
        else:
            groups = None
                
        group_name = self.args.group_name if self.args.group_name else 'group'

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)

        for i, f in enumerate(self.args.files):
            rows = CSVKitReader(f, **self.reader_kwargs)
            headers = rows.next()

            if i == 0:
                if groups:
                    headers.insert(0, group_name)
                
                output.writerow(headers)

            for row in rows:
                if groups:
                    row.insert(0, groups[i])

                output.writerow(row)

if __name__ == '__main__':
    CSVStack().main()

