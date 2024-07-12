#!/usr/bin/env python

import sys

import agate

from csvkit.cleanup import RowChecker
from csvkit.cli import CSVKitUtility


class CSVClean(CSVKitUtility):
    description = 'Report and fix common errors in a CSV file.'
    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument(
            '--length-mismatch', dest='length_mismatch', action='store_true',
            help='Report data rows that are shorter or longer than the header row.')
        self.argparser.add_argument(
            '--empty-columns', dest='empty_columns', action='store_true',
            help='Report empty columns as errors.')
        self.argparser.add_argument(
            '-a', '--enable-all-checks', dest='enable_all_checks', action='store_true',
            help='Enable all error reporting.')
        self.argparser.add_argument(
            '--omit-error-rows', dest='omit_error_rows', action='store_true',
            help='Omit data rows that contain errors, from standard output.')
        self.argparser.add_argument(
            '--label', dest='label',
            help='Add a "label" column to standard error. Useful in automated workflows. '
                 'Use "-" to default to the input filename.')
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

    def main(self):
        if self.additional_input_expected():
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        if (
            # Checks
            not self.args.length_mismatch
            and not self.args.empty_columns
            and not self.args.enable_all_checks
            # Fixes
            and not self.args.header_normalize_space
            and not self.args.join_short_rows
            and not self.args.fill_short_rows
        ):
            self.argparser.error('No checks or fixes were enabled. See available options with: csvclean --help')

        if self.args.join_short_rows and self.args.fill_short_rows:
            self.argparser.error('The --join-short-rows and --fill-short-rows options are mutually exclusive.')

        default = self.args.enable_all_checks

        reader = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)

        checker = RowChecker(
            reader,
            # Checks
            length_mismatch=default or self.args.length_mismatch,
            empty_columns=default or self.args.empty_columns,
            # Fixes
            header_normalize_space=self.args.header_normalize_space,
            join_short_rows=self.args.join_short_rows,
            separator=self.args.separator,
            fill_short_rows=self.args.fill_short_rows,
            fillvalue=self.args.fillvalue,
            # Other
            zero_based=self.args.zero_based,
            omit_error_rows=self.args.omit_error_rows,
        )

        label = self.args.label
        if label == '-':
            if self.input_file == sys.stdin:
                label = 'stdin'
            else:
                label = self.input_file.name

        output_writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        output_writer.writerow(checker.column_names)
        for row in checker.checked_rows():
            output_writer.writerow(row)

        if checker.errors:
            error_writer = agate.csv.writer(self.error_file, **self.writer_kwargs)

            fieldnames = ['line_number', 'msg'] + checker.column_names
            if self.args.label:
                fieldnames.insert(0, 'label')
            error_writer.writerow(fieldnames)

            for error in checker.errors:
                row = [error.line_number, error.msg] + error.row
                if self.args.label:
                    row.insert(0, label)
                error_writer.writerow(row)

            sys.exit(1)


def launch_new_instance():
    utility = CSVClean()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
