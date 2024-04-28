#!/usr/bin/env python

import sys

import agate

from csvkit.cleanup import RowChecker
from csvkit.cli import CSVKitUtility


class CSVClean(CSVKitUtility):
    description = 'Fix common errors in a CSV file.'
    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument(
            '--header-normalize-space', dest='header_normalize_space', action='store_true',
            help='Strip leading and trailing whitespace and replace sequences of whitespace characters by a single '
                 'space in the header.')
        self.argparser.add_argument(
            '--join-short-rows', dest='join_short_rows', action='store_true',
            help='Merges short rows into a single row.')
        self.argparser.add_argument(
            '--separator', dest='separator', default='\n',
            help='The string with which to join short rows. Defaults to a newline.')
        self.argparser.add_argument(
            '--fill-short-rows', dest='fill_short_rows', action='store_true',
            help='Fill short rows with the missing cells.')
        self.argparser.add_argument(
            '--fillvalue', dest='fillvalue',
            help='The value with which to fill short rows. Defaults to none.')
        self.argparser.add_argument(
            '--empty-columns', dest='empty_columns', action='store_true',
            help='Report empty columns as errors.')

    def main(self):
        if self.additional_input_expected():
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        if self.args.join_short_rows and self.args.fill_short_rows:
            self.argparser.error('The --join-short-rows and --fill-short-rows options are mutually exclusive.')

        reader = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)

        checker = RowChecker(
            reader,
            header_normalize_space=self.args.header_normalize_space,
            join_short_rows=self.args.join_short_rows,
            separator=self.args.separator,
            fill_short_rows=self.args.fill_short_rows,
            fillvalue=self.args.fillvalue,
            empty_columns=self.args.empty_columns,
            zero_based=self.args.zero_based,
        )

        output_writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        output_writer.writerow(checker.column_names)
        for row in checker.checked_rows():
            output_writer.writerow(row)

        if checker.errors:
            error_writer = agate.csv.writer(self.error_file, **self.writer_kwargs)
            error_writer.writerow(['line_number', 'msg'] + checker.column_names)
            for error in checker.errors:
                error_writer.writerow([error.line_number, error.msg] + error.row)

            sys.exit(1)


def launch_new_instance():
    utility = CSVClean()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
