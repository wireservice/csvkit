#!/usr/bin/env python

import sys
from os.path import splitext

import agate

from csvkit.cli import CSVKitUtility
from csvkit.cleanup import RowChecker


class CSVClean(CSVKitUtility):
    description = 'Fix common errors in a CSV file.'
    override_flags = ['H']

    def add_arguments(self):
        self.argparser.add_argument('-n', '--dry-run', dest='dryrun', action='store_true',
                                    help='Do not create output files. Information about what would have been done will be printed to STDERR.')

    def main(self):
        reader = agate.csv.reader(self.input_file, **self.reader_kwargs)

        if self.args.dryrun:
            checker = RowChecker(reader)

            for row in checker.checked_rows():
                pass

            if checker.errors:
                for e in checker.errors:
                    self.output_file.write('Line %i: %s\n' % (e.line_number, e.msg))
            else:
                self.output_file.write('No errors.\n')

            if checker.joins:
                self.output_file.write('%i rows would have been joined/reduced to %i rows after eliminating expected internal line breaks.\n' % (checker.rows_joined, checker.joins))
        else:
            if self.input_file == sys.stdin:
                base = 'stdin'  # "<stdin>_out.csv" is invalid on Windows
            else:
                base = splitext(self.input_file.name)[0]

            with open('%s_out.csv' % base, 'w') as f:
                clean_writer = agate.csv.writer(f, **self.writer_kwargs)

                checker = RowChecker(reader)
                clean_writer.writerow(checker.column_names)

                for row in checker.checked_rows():
                    clean_writer.writerow(row)

            if checker.errors:
                error_filename = '%s_err.csv' % base

                with open(error_filename, 'w') as f:
                    error_writer = agate.csv.writer(f, **self.writer_kwargs)

                    error_header = ['line_number', 'msg']
                    error_header.extend(checker.column_names)
                    error_writer.writerow(error_header)

                    error_count = len(checker.errors)

                    for e in checker.errors:
                        error_writer.writerow(self._format_error_row(e))

                self.output_file.write('%i error%s logged to %s\n' % (error_count, '' if error_count == 1 else 's', error_filename))
            else:
                self.output_file.write('No errors.\n')

            if checker.joins:
                self.output_file.write('%i rows were joined/reduced to %i rows after eliminating expected internal line breaks.\n' % (checker.rows_joined, checker.joins))

    def _format_error_row(self, error):
        row = [error.line_number, error.msg]
        row.extend(error.row)

        return row


def launch_new_instance():
    utility = CSVClean()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
