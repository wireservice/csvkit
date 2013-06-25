#!/usr/bin/env python

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.group import group_rows, aggregate_functions


class CSVGroup(CSVKitUtility):
    description = 'Execute a SQL-like group by on specified column or columns'

    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='The column name(s) on which to group by. Should be either one name (or index) or a comma-separated list. May also be left unspecified, in which case none columns will be used')

        self.argparser.add_argument('-a', '--aggregation', dest='aggregations',
                                    nargs=2, metavar=('FUNCTION', 'COLUMNS'),
                                    action='append',
                                    help='Aggregate column values using max function')

        self.argparser.add_argument('-n', '--names', dest='names_only',
                                    action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        #Read in header and rows
        reader = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = reader.next()
        if self.args.columns is None:
            grouped_columns_ids = []
        else:
            grouped_columns_ids = parse_column_identifiers(self.args.columns,
                                                       column_names,
                                                       self.args.zero_based)
        aggregations = []
        try:
            for (fun, cols) in map(lambda (f, cols): (
            f, parse_column_identifiers(cols, column_names, self.args.zero_based)),
                                   self.args.aggregations):
                for col in cols:
                    aggregations.append(aggregate_functions[fun](col))
        except KeyError:
            self.argparser.error("Wrong aggregator function. Available: " + ', '.join(aggregate_functions.keys()))
        #Determine columns to group by, default to all columns


        #Write the output
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        for row in group_rows(column_names, reader, grouped_columns_ids,
                              aggregations):
            output.writerow(row)


def launch_new_instance():
    utility = CSVGroup()
    utility.main()


if __name__ == "__main__":
    launch_new_instance()
