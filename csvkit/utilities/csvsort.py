#!/usr/bin/env python

from functools import cmp_to_key

import agate

from csvkit.cli import CSVKitUtility, match_column_identifier, parse_column_identifiers


def ignore_case_sort(key):

    def inner(row):
        return tuple(
            agate.NullOrder() if row[n] is None else (row[n].upper() if isinstance(row[n], str) else row[n])
            for n in key
        )

    return inner


def mixed_direction_sort(columns, descending, ignore_case):

    def compare_rows(left, right):
        for column, is_descending in zip(columns, descending):
            left_value = left[column]
            right_value = right[column]

            if ignore_case:
                if isinstance(left_value, str):
                    left_value = left_value.upper()
                if isinstance(right_value, str):
                    right_value = right_value.upper()

            if left_value is None:
                left_value = agate.NullOrder()
            if right_value is None:
                right_value = agate.NullOrder()

            comparison = (left_value > right_value) - (left_value < right_value)
            if comparison:
                return -comparison if is_descending else comparison

        return 0

    return cmp_to_key(compare_rows)


class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like the Unix "sort" command, but for tabular data.'
    literal_options = ('-c', '--columns')

    def add_arguments(self):
        self.argparser.add_argument(
            '-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument(
            '-c', '--columns', dest='columns',
            help='A comma-separated list of column indices, names or ranges to sort by, e.g. "1,id,3-5". '
                 'Prefix a column with "~" to sort it in descending order. Defaults to all columns.')
        self.argparser.add_argument(
            '-r', '--reverse', dest='reverse', action='store_true',
            help='Reverse the sort direction of every column.')
        self.argparser.add_argument(
            '-i', '--ignore-case', dest='ignore_case', action='store_true',
            help='Perform case-independent sorting.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference (and --locale, --date-format, --datetime-format, --no-leading-zeroes) '
                 'when parsing the input.')

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

        identifiers = self.args.columns.split(',') if self.args.columns else []
        reverse_columns = [
            identifier.startswith('~') and len(identifier) > 1 and identifier not in table.column_names
            for identifier in identifiers
        ]

        if any(reverse_columns):
            columns = []
            descending = []
            for identifier, is_descending in zip(identifiers, reverse_columns):
                if not identifier:
                    selected = [match_column_identifier(table.column_names, identifier, self.get_column_offset())]
                else:
                    selected = parse_column_identifiers(
                        identifier[1:] if is_descending else identifier,
                        table.column_names,
                        self.get_column_offset(),
                    )
                columns.extend(selected)
                descending.extend([is_descending] * len(selected))
        else:
            columns = parse_column_identifiers(self.args.columns, table.column_names, self.get_column_offset())
            descending = []

        if any(descending):
            key = mixed_direction_sort(columns, descending, self.args.ignore_case)
        elif self.args.ignore_case:
            key = ignore_case_sort(columns)
        else:
            key = columns

        table = table.order_by(key, reverse=self.args.reverse)
        table.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVSort()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
