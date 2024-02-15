#!/usr/bin/env python
import itertools
import sys

import agate

from csvkit.cli import CSVKitUtility, make_default_headers


class CSVFormat(CSVKitUtility):
    description = 'Convert a CSV file to a custom output format.'
    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument(
            '-E', '--skip-header', dest='skip_header', action='store_true',
            help='Do not output a header row.')
        self.argparser.add_argument(
            '-D', '--out-delimiter', dest='out_delimiter',
            help='Delimiting character of the output file.')
        self.argparser.add_argument(
            '-T', '--out-tabs', dest='out_tabs', action='store_true',
            help='Specify that the output file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument(
            '-A', '--out-asv', dest='out_asv', action='store_true',
            help='Specify that the output file is delimited with the ASCII unit separator and record separator. '
                 'Overrides "-T", "-D" and "-M".')
        self.argparser.add_argument(
            '-Q', '--out-quotechar', dest='out_quotechar',
            help='Character used to quote strings in the output file.')
        self.argparser.add_argument(
            '-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3],
            help='Quoting style used in the output file. 0 = Quote Minimal, 1 = Quote All, '
                 '2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument(
            '-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
            help='Whether or not double quotes are doubled in the output file.')
        self.argparser.add_argument(
            '-P', '--out-escapechar', dest='out_escapechar',
            help='Character used to escape the delimiter in the output file if --quoting 3 ("Quote None") is '
                 'specified and to escape the QUOTECHAR if --out-no-doublequote is specified.')
        self.argparser.add_argument(
            '-M', '--out-lineterminator', dest='out_lineterminator',
            help='Character used to terminate lines in the output file.')

    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        if self.args.line_numbers:
            kwargs['line_numbers'] = True

        if self.args.out_asv:
            kwargs['delimiter'] = '\x1f'
        elif self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter

        if self.args.out_asv:
            kwargs['lineterminator'] = '\x1e'
        elif self.args.out_lineterminator:
            kwargs['lineterminator'] = self.args.out_lineterminator

        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar'):
            value = getattr(self.args, f'out_{arg}')
            if value is not None:
                kwargs[arg] = value

        return kwargs

    def main(self):
        if self.additional_input_expected():
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        reader = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        if self.args.no_header_row:
            # Peek at a row to get the number of columns.
            _row = next(reader)
            headers = make_default_headers(len(_row))
            reader = itertools.chain([headers, _row], reader)

        if self.args.skip_header:
            next(reader)

        writer.writerows(reader)


def launch_new_instance():
    utility = CSVFormat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
