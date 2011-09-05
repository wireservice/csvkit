#!/usr/bin/env python

import os

from csvkit import CSVKitWriter
from csvkit import table
from csvkit.cli import CSVKitUtility, parse_column_identifiers, print_column_names

class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like unix "sort" command, but for tabular data.'

    def add_arguments(self):        
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes.')
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                            help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                help='Sort in descending order.')

    def main(self):
        if self.args.names_only:
            print_column_names(self.args.file, self.output_file, **self.reader_kwargs)
            return

        if self.args.file.name != '<stdin>':
            # Use filename as table name
            table_name = os.path.splitext(os.path.split(self.args.file.name)[1])[0]
        else:
            table_name = 'csvsql_table'

        tab = table.Table.from_csv(self.args.file, name=table_name, snifflimit=self.args.snifflimit, **self.reader_kwargs)
        column_ids = parse_column_identifiers(self.args.columns, tab.headers())

        rows = tab.to_rows(serialize_dates=True) 
        rows.sort(key=lambda r: [r[c] for c in column_ids], reverse=self.args.reverse)
        
        rows.insert(0, tab.headers())

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)

        for row in rows:
            output.writerow(row)
                
if __name__ == "__main__":
    utility = CSVSort()
    utility.main()
