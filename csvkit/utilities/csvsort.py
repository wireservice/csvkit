#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility, parse_column_identifiers


class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like the Unix "sort" command, but for tabular data.'
    buffers_input = True

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to sort by. Defaults to all columns.')
        self.argparser.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                                    help='Sort in descending order.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        table = agate.Table.from_csv(
            self.input_file,
            sniff_limit=self.args.sniff_limit,
            header=not self.args.no_header_row,
            column_types=self.get_column_types(),
            **self.reader_kwargs
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset()
        )

        table = table.order_by(column_ids, reverse=self.args.reverse)
        table.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVSort()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
