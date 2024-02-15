#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility, parse_column_identifiers


def ignore_case_sort(key):

    def inner(row):
        return tuple(
            agate.NullOrder() if row[n] is None else (row[n].upper() if isinstance(row[n], str) else row[n])
            for n in key
        )

    return inner


class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like the Unix "sort" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument(
            '-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument(
            '-c', '--columns', dest='columns',
            help='A comma-separated list of column indices, names or ranges to sort by, e.g. "1,id,3-5". '
                 'Defaults to all columns.')
        self.argparser.add_argument(
            '-r', '--reverse', dest='reverse', action='store_true',
            help='Sort in descending order.')
        self.argparser.add_argument(
            '-i', '--ignore-case', dest='ignore_case', action='store_true',
            help='Perform case-independent sorting.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=sniff_limit,
            column_types=self.get_column_types(),
            **self.reader_kwargs,
        )

        key = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset(),
        )

        if self.args.ignore_case:
            key = ignore_case_sort(key)

        table = table.order_by(key, reverse=self.args.reverse)
        table.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVSort()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
