#!/usr/bin/env python

import os

from csvkit import CSVKitWriter
from csvkit import table
from csvkit.cli import CSVKitUtility, parse_column_identifiers

class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like unix "sort" command, but for tabular data.'

    def add_arguments(self):        
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='A comma separated list of column indices or names to sort by. Defaults to all columns.')
        self.argparser.add_argument('-r', '--reverse', dest='reverse', action='store_true',
            help='Sort in descending order.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.input_file.name != '<stdin>':
            # Use filename as table name
            table_name = os.path.splitext(os.path.split(self.input_file.name)[1])[0]
        else:
            table_name = 'csvsql_table'

        tab = table.Table.from_csv(
            self.input_file,
            name=table_name,
            snifflimit=self.args.snifflimit,
            no_header_row=self.args.no_header_row,
            infer_types=(not self.args.no_inference),
            **self.reader_kwargs
        )
        
        column_ids = parse_column_identifiers(self.args.columns, tab.headers(), self.args.zero_based)

        rows = tab.to_rows(serialize_dates=True) 
        sorter = lambda r: [(r[c] is not None, r[c]) for c in column_ids]
        rows.sort(key=sorter, reverse=self.args.reverse)
        
        rows.insert(0, tab.headers())

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)

        for row in rows:
            output.writerow(row)

def launch_new_instance():
    utility = CSVSort()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

