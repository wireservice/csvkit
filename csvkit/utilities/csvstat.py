#!/usr/bin/env python

import json
import locale
import warnings
from collections import Counter, OrderedDict
from decimal import Decimal

import agate

from csvkit.cli import CSVKitUtility, default_float_decimal, parse_column_identifiers

locale.setlocale(locale.LC_ALL, '')
OPERATIONS = OrderedDict([
    ('type', {
        'aggregation': None,
        'label': 'Type of data: ',
    }),
    ('nulls', {
        'aggregation': agate.HasNulls,
        'label': 'Contains null values: ',
    }),
    ('nonnulls', {
        'aggregation': agate.Count,
        'label': 'Non-null values: ',
    }),
    ('unique', {
        'aggregation': None,
        'label': 'Unique values: ',
    }),
    ('min', {
        'aggregation': agate.Min,
        'label': 'Smallest value: ',
    }),
    ('max', {
        'aggregation': agate.Max,
        'label': 'Largest value: ',
    }),
    ('sum', {
        'aggregation': agate.Sum,
        'label': 'Sum: ',
    }),
    ('mean', {
        'aggregation': agate.Mean,
        'label': 'Mean: ',
    }),
    ('median', {
        'aggregation': agate.Median,
        'label': 'Median: ',
    }),
    ('stdev', {
        'aggregation': agate.StDev,
        'label': 'StDev: ',
    }),
    ('len', {
        'aggregation': agate.MaxLength,
        'label': 'Longest value: ',
    }),
    ('maxprecision', {
        'aggregation': agate.MaxPrecision,
        'label': 'Most decimal places: ',
    }),
    ('freq', {
        'aggregation': None,
        'label': 'Most common values: ',
    }),
])


class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'

    def add_arguments(self):
        self.argparser.add_argument(
            '--csv', dest='csv_output', action='store_true',
            help='Output results as a CSV table, rather than plain text.')
        self.argparser.add_argument(
            '--json', dest='json_output', action='store_true',
            help='Output results as JSON text, rather than plain text.')
        self.argparser.add_argument(
            '-i', '--indent', dest='indent', type=int,
            help='Indent the output JSON this many spaces. Disabled by default.')
        self.argparser.add_argument(
            '-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument(
            '-c', '--columns', dest='columns',
            help='A comma-separated list of column indices, names or ranges to be examined, e.g. "1,id,3-5". '
                 'Defaults to all columns.')
        self.argparser.add_argument(
            '--type', dest='type_only', action='store_true',
            help='Only output data type.')
        self.argparser.add_argument(
            '--nulls', dest='nulls_only', action='store_true',
            help='Only output whether columns contains nulls.')
        self.argparser.add_argument(
            '--non-nulls', dest='nonnulls_only', action='store_true',
            help='Only output counts of non-null values.')
        self.argparser.add_argument(
            '--unique', dest='unique_only', action='store_true',
            help='Only output counts of unique values.')
        self.argparser.add_argument(
            '--min', dest='min_only', action='store_true',
            help='Only output smallest values.')
        self.argparser.add_argument(
            '--max', dest='max_only', action='store_true',
            help='Only output largest values.')
        self.argparser.add_argument(
            '--sum', dest='sum_only', action='store_true',
            help='Only output sums.')
        self.argparser.add_argument(
            '--mean', dest='mean_only', action='store_true',
            help='Only output means.')
        self.argparser.add_argument(
            '--median', dest='median_only', action='store_true',
            help='Only output medians.')
        self.argparser.add_argument(
            '--stdev', dest='stdev_only', action='store_true',
            help='Only output standard deviations.')
        self.argparser.add_argument(
            '--len', dest='len_only', action='store_true',
            help='Only output the length of the longest values.')
        self.argparser.add_argument(
            '--max-precision', dest='maxprecision_only', action='store_true',
            help='Only output the most decimal places.')
        self.argparser.add_argument(
            '--freq', dest='freq_only', action='store_true',
            help='Only output lists of frequent values.')
        self.argparser.add_argument(
            '--freq-count', dest='freq_count', type=int,
            help='The maximum number of frequent values to display.')
        self.argparser.add_argument(
            '--count', dest='count_only', action='store_true',
            help='Only output total row count.')
        self.argparser.add_argument(
            '--decimal-format', dest='decimal_format', type=str, default='%.3f',
            help='%%-format specification for printing decimal numbers. '
                 'Defaults to locale-specific formatting with "%%.3f".')
        self.argparser.add_argument(
            '-G', '--no-grouping-separator', dest='no_grouping_separator', action='store_true',
            help='Do not use grouping separators in decimal numbers.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input. Disable reformatting of values.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        operations = [op for op in OPERATIONS.keys() if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one operation argument may be specified (--mean, --median, etc).')

        if operations and self.args.csv_output:
            self.argparser.error(
                'You may not specify --csv and an operation (--mean, --median, etc) at the same time.')
        if operations and self.args.json_output:
            self.argparser.error(
                'You may not specify --json and an operation (--mean, --median, etc) at the same time.')
        if operations and self.args.count_only:
            self.argparser.error(
                'You may not specify --count and an operation (--mean, --median, etc) at the same time.')

        if self.args.count_only:
            count = len(list(agate.csv.reader(self.skip_lines(), **self.reader_kwargs)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('%i\n' % count)

            return

        sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=sniff_limit,
            column_types=self.get_column_types(),
            **self.reader_kwargs,
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset(),
        )

        kwargs = {}

        if self.args.freq_count:
            kwargs['freq_count'] = self.args.freq_count

        # Output a single stat
        if operations:
            if len(column_ids) == 1:
                self.print_one(table, column_ids[0], operations[0], label=False, **kwargs)
            else:
                for column_id in column_ids:
                    self.print_one(table, column_id, operations[0], **kwargs)
        else:
            stats = {}

            for column_id in column_ids:
                stats[column_id] = self.calculate_stats(table, column_id, **kwargs)

            if self.args.csv_output:
                self.print_csv(table, column_ids, stats)
            elif self.args.json_output:
                self.print_json(table, column_ids, stats)
            else:
                self.print_stats(table, column_ids, stats)

    def is_finite_decimal(self, value):
        return isinstance(value, Decimal) and value.is_finite()

    def _calculate_stat(self, table, column_id, op_name, op_data, **kwargs):
        getter = globals().get(f'get_{op_name}')

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', agate.NullCalculationWarning)

            try:
                if getter:
                    return getter(table, column_id, **kwargs)

                op = op_data['aggregation']
                v = table.aggregate(op(column_id))

                if self.is_finite_decimal(v) and not self.args.json_output:
                    return format_decimal(v, self.args.decimal_format, self.args.no_grouping_separator)

                return v
            except Exception:
                pass

    def print_one(self, table, column_id, op_name, label=True, **kwargs):
        """
        Print data for a single statistic.
        """
        column_name = table.column_names[column_id]

        stat = self._calculate_stat(table, column_id, op_name, OPERATIONS[op_name], **kwargs)

        # Formatting
        if op_name == 'freq':
            stat = ', '.join([f"\"{str(row['value'])}\": {row['count']}" for row in stat])
            stat = '{ %s }' % stat

        if label:
            self.output_file.write('%3i. %s: %s\n' % (column_id + 1, column_name, stat))
        else:
            self.output_file.write(f'{stat}\n')

    def calculate_stats(self, table, column_id, **kwargs):
        """
        Calculate stats for all valid operations.
        """
        return {
            op_name: self._calculate_stat(table, column_id, op_name, op_data, **kwargs)
            for op_name, op_data in OPERATIONS.items()
        }

    def print_stats(self, table, column_ids, stats):
        """
        Print data for all statistics.
        """
        label_column_width = max(len(op_data['label']) for op_data in OPERATIONS.values())

        for column_id in column_ids:
            column_name = table.column_names[column_id]
            column = table.columns[column_id]
            column_stats = stats[column_id]

            self.output_file.write('%3i. "%s"\n\n' % (column_id + 1, column_name))

            for op_name, op_data in OPERATIONS.items():
                if column_stats[op_name] is None:
                    continue

                label = '{label:{label_column_width}}'.format(**{
                    'label_column_width': label_column_width,
                    'label': op_data['label'],
                })

                if op_name == 'freq':
                    for i, row in enumerate(column_stats['freq']):
                        if i == 0:
                            self.output_file.write(f'\t{label} ')
                        else:
                            self.output_file.write('\t{label:{label_column_width}} '.format(**{
                                'label_column_width': label_column_width,
                                'label': '',
                            }))

                        if isinstance(column.data_type, agate.Number):
                            v = row['value']

                            if self.is_finite_decimal(v):
                                v = format_decimal(v, self.args.decimal_format, self.args.no_grouping_separator)
                        else:
                            v = str(row['value'])

                        self.output_file.write(f"{v} ({row['count']}x)\n")

                    continue

                v = column_stats[op_name]

                if op_name == 'nulls' and v:
                    v = f'{v} (excluded from calculations)'
                elif op_name == 'len':
                    v = f'{v} characters'

                self.output_file.write(f'\t{label} {v}\n')

            self.output_file.write('\n')

        self.output_file.write(f'Row count: {len(table.rows)}\n')

    def print_csv(self, table, column_ids, stats):
        """
        Print data for all statistics as a CSV table.
        """
        header = ['column_id', 'column_name'] + list(OPERATIONS)

        writer = agate.csv.DictWriter(self.output_file, fieldnames=header)
        writer.writeheader()

        for row in self._rows(table, column_ids, stats):
            if 'freq' in row:
                row['freq'] = ', '.join([str(row['value']) for row in row['freq']])
            writer.writerow(row)

    def print_json(self, table, column_ids, stats):
        """
        Print data for all statistics as a JSON text.
        """
        data = list(self._rows(table, column_ids, stats))

        json.dump(data, self.output_file, default=default_float_decimal, ensure_ascii=False, indent=self.args.indent)

    def _rows(self, table, column_ids, stats):
        for column_id in column_ids:
            column_name = table.column_names[column_id]
            column_stats = stats[column_id]

            output_row = {'column_id': column_id + 1, 'column_name': column_name}
            for op_name, _op_data in OPERATIONS.items():
                if column_stats[op_name] is not None:
                    output_row[op_name] = column_stats[op_name]

            yield output_row


def format_decimal(d, f='%.3f', no_grouping_separator=False):
    return locale.format_string(f, d, grouping=not no_grouping_separator).rstrip('0').rstrip('.')


# These are accessed via: globals().get(f'get_{op_name}')
def get_type(table, column_id, **kwargs):
    return f'{table.columns[column_id].data_type.__class__.__name__}'


def get_unique(table, column_id, **kwargs):
    return len(table.columns[column_id].values_distinct())


def get_freq(table, column_id, freq_count=5, **kwargs):
    values = table.columns[column_id].values()
    return [
        {'value': r[0], 'count': r[1]}
        for r in Counter(values).most_common(freq_count)
    ]


def launch_new_instance():
    utility = CSVStat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
