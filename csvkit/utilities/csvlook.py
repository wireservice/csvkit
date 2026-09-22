#!/usr/bin/env python

import math

import agate
from agate import config, utils
from babel.numbers import format_decimal

from csvkit.cli import CSVKitUtility


class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a Markdown-compatible, fixed-width table.'

    def add_arguments(self):
        self.argparser.add_argument(
            '--expanded', action='store_true',
            help='Display each record vertically, with one field per line.')
        self.argparser.add_argument(
            '--max-rows', dest='max_rows', type=int,
            help='The maximum number of rows to display before truncating the data.')
        self.argparser.add_argument(
            '--max-columns', dest='max_columns', type=int,
            help='The maximum number of columns to display before truncating the data.')
        self.argparser.add_argument(
            '--max-column-width', dest='max_column_width', type=int,
            help='Truncate all columns to at most this width. The remainder will be replaced with ellipsis.')
        self.argparser.add_argument(
            '--max-precision', dest='max_precision', type=int,
            help='The maximum number of decimal places to display. The remainder will be replaced with ellipsis.')
        self.argparser.add_argument(
            '--no-number-ellipsis', dest='no_number_ellipsis', action='store_true',
            help='Disable the ellipsis if --max-precision is exceeded.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference (and --locale, --date-format, --datetime-format, --no-leading-zeroes) '
                 'when parsing the input.')

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        kwargs = {}
        # In agate, max_precision defaults to 3. None means infinity.
        if self.args.max_precision is not None:
            kwargs['max_precision'] = self.args.max_precision

        if self.args.no_number_ellipsis:
            config.set_option('number_truncation_chars', '')

        sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=sniff_limit,
            row_limit=self.args.max_rows,
            column_types=self.get_column_types(),
            line_numbers=self.args.line_numbers,
            **self.reader_kwargs,
        )

        if self.args.expanded:
            self.print_expanded(table, **kwargs)
            return

        table.print_table(
            output=self.output_file,
            max_rows=self.args.max_rows,
            max_columns=self.args.max_columns,
            max_column_width=self.args.max_column_width,
            **kwargs,
        )

    def print_expanded(self, table, max_precision=3):
        """Display records vertically, retaining csvlook's numeric formatting."""
        columns = table.columns[:self.args.max_columns]
        ellipsis = config.get_option('ellipsis_chars')
        truncation = config.get_option('text_truncation_chars')
        separator = config.get_option('vertical_line_char')
        locale = config.get_option('default_locale')

        def format_text(value):
            text = str(value).replace('\r\n', '\n').replace('\r', '\n').replace('\n', '↵').replace('\t', '⇥')
            width = self.args.max_column_width
            if width is not None and len(text) > width:
                text = text[:max(0, width - len(truncation))] + truncation
            return text

        names = [format_text(column.name) for column in columns]
        columns_truncated = len(columns) < len(table.columns)
        if columns_truncated:
            names.append(ellipsis)
        name_width = max((len(name) for name in names), default=0)

        # Determine precision per source column, just as print_table does.
        formatters = []
        for column in columns:
            if isinstance(column.data_type, agate.Number):
                places = utils.max_precision(column)
                formatters.append(utils.make_number_formatter(min(places, max_precision), places > max_precision))
            else:
                formatters.append(None)

        for record_number, row in enumerate(table.rows, 1):
            self.output_file.write(f'-[ RECORD {record_number} ]-\n')
            for index, (name, formatter) in enumerate(zip(names, formatters)):
                value = row[index]
                if value is None:
                    text = ''
                elif formatter is not None and not math.isinf(value):
                    text = format_text(format_decimal(value, format=formatter, locale=locale))
                else:
                    text = format_text(value)
                self.output_file.write(f'{name.ljust(name_width)} {separator} {text}\n')
            if columns_truncated:
                self.output_file.write(f'{ellipsis.ljust(name_width)} {separator} {ellipsis}\n')


def launch_new_instance():
    utility = CSVLook()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
