#!/usr/bin/env python

import codecs
from collections import OrderedDict
import warnings

import agate
from babel.numbers import format_decimal
import six

from csvkit.cli import CSVKitUtility, parse_column_identifiers

NoneType = type(None)

MAX_UNIQUE = 5
MAX_FREQ = 5

OPERATIONS = OrderedDict([
    ('type', {
        'aggregation': None,
        'label': 'Type of data: '
    }),
    ('nulls', {
        'aggregation': agate.HasNulls,
        'label': 'Contains null values: '
    }),
    ('unique', {
        'aggregation': None,
        'label': 'Unique values: '
    }),
    ('min', {
        'aggregation': agate.Min,
        'label': 'Smallest value: '
    }),
    ('max', {
        'aggregation': agate.Max,
        'label': 'Largest value: '
    }),
    ('sum', {
        'aggregation': agate.Sum,
        'label': 'Sum: '
    }),
    ('mean', {
        'aggregation': agate.Mean,
        'label': 'Mean: '
    }),
    ('median', {
        'aggregation': agate.Median,
        'label': 'Median: '
    }),
    ('stdev', {
        'aggregation': agate.StDev,
        'label': 'StDev: '
    }),
    ('len', {
        'aggregation': agate.MaxLength,
        'label': 'Longest value: '
    }),
    ('freq', {
        'aggregation': None,
        'label': 'Most common values: '
    })
])


class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = ['l']

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to be examined. Defaults to all columns.')
        self.argparser.add_argument('--type', dest='type_only', action='store_true',
                                    help='Only output data type.')
        self.argparser.add_argument('--nulls', dest='nulls_only', action='store_true',
                                    help='Only output whether columns contains nulls.')
        self.argparser.add_argument('--unique', dest='unique_only', action='store_true',
                                    help='Only output counts of unique values.')
        self.argparser.add_argument('--min', dest='min_only', action='store_true',
                                    help='Only output smallest values.')
        self.argparser.add_argument('--max', dest='max_only', action='store_true',
                                    help='Only output largest values.')
        self.argparser.add_argument('--sum', dest='sum_only', action='store_true',
                                    help='Only output sums.')
        self.argparser.add_argument('--mean', dest='mean_only', action='store_true',
                                    help='Only output means.')
        self.argparser.add_argument('--median', dest='median_only', action='store_true',
                                    help='Only output medians.')
        self.argparser.add_argument('--stdev', dest='stdev_only', action='store_true',
                                    help='Only output standard deviations.')
        self.argparser.add_argument('--len', dest='len_only', action='store_true',
                                    help='Only output the length of the longest values.')
        self.argparser.add_argument('--freq', dest='freq_only', action='store_true',
                                    help='Only output lists of frequent values.')
        self.argparser.add_argument('--count', dest='count_only', action='store_true',
                                    help='Only output total row count')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        operations = [op for op in OPERATIONS.keys() if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one operation argument may be specified (--mean, --median, etc).')

        if operations and self.args.count_only:
            self.argparser.error('You may not specify --count and an operation (--mean, --median, etc) at the same time.')

        if six.PY2:
            self.output_file = codecs.getwriter('utf-8')(self.output_file)

        if self.args.count_only:
            count = len(list(agate.csv.reader(self.input_file)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('Row count: %i\n' % count)

            return

        table = agate.Table.from_csv(
            self.input_file,
            sniff_limit=self.args.sniff_limit,
            header=not self.args.no_header_row,
            **self.reader_kwargs
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset()
        )

        for column_id in column_ids:
            column_name = table.column_names[column_id]
            column = table.columns[column_id]

            # Output a single stat
            if len(operations) == 1:
                op_name = operations[0]
                getter = globals().get('get_%s' % op_name, None)

                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', agate.NullCalculationWarning)

                    try:
                        if getter:
                            stat = getter(table, column_name)
                        else:
                            op = OPERATIONS[op_name]['aggregation']
                            stat = format_decimal(table.aggregate(op(column_name)))
                    except:
                        stat = None

                # Formatting
                if op_name == 'freq':
                    stat = ', '.join([(u'"%s": %s' % (six.text_type(row[column_name]), row['Count'])) for row in stat])
                    stat = u'{ %s }' % stat

                if len(table.columns) == 1:
                    self.output_file.write(six.text_type(stat))
                else:
                    self.output_file.write(u'%3i. %s: %s\n' % (column_id + 1, column_name, stat))
            # Output all stats
            else:
                stats = {}

                label_column_width = 0
                freq_value_width = 0

                for op_name, op_data in OPERATIONS.items():
                    label_column_width = max(label_column_width, len(op_data['label']))

                    getter = globals().get('get_%s' % op_name, None)

                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', agate.NullCalculationWarning)

                        try:
                            if getter:
                                stats[op_name] = getter(table, column_name)
                            else:
                                op = op_data['aggregation']
                                stats[op_name] = format_decimal(table.aggregate(op(column_name)))
                        except:
                            stats[op_name] = None

                self.output_file.write(('%3i. "%s"\n\n' % (column_id + 1, column_name)))

                for op_name, op_data in OPERATIONS.items():
                    if not stats[op_name]:
                        continue

                    label = u'{label:{label_column_width}}'.format(**{
                        'label_column_width': label_column_width,
                        'label': op_data['label']
                    })

                    if op_name == 'freq':
                        for i, row in enumerate(stats['freq']):
                            if i == 0:
                                self.output_file.write('\t{} '.format(label))
                            else:
                                self.output_file.write(u'\t{label:{label_column_width}} '.format(**{
                                    'label_column_width': label_column_width,
                                    'label': ''
                                }))

                            if isinstance(column.data_type, agate.Number):
                                v = format_decimal(row[column_name])
                            else:
                                v = six.text_type(row[column_name])

                            self.output_file.write(u'{} ({}x)\n'.format(v, row['Count']))

                        continue

                    self.output_file.write(u'\t{} {}\n'.format(label, stats[op_name]))

                self.output_file.write('\n')

        if not operations:
            self.output_file.write('Row count: %s\n' % len(table.rows))


def get_type(table, column_name):
    return '%s' % table.columns[column_name].data_type.__class__.__name__


def get_nulls(table, column_name):
    if table.aggregate(agate.HasNulls(column_name)):
        return 'True (excluded from calculations)'
    else:
        return 'False'


def get_unique(table, column_name):
    return len(table.columns[column_name].values_distinct())


def get_len(table, column_name):
    return '%s characters' % table.aggregate(agate.MaxLength(column_name))


def get_freq(table, column_name):
    return table.pivot(column_name).order_by('Count', reverse=True).limit(MAX_FREQ)


def launch_new_instance():
    utility = CSVStat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
