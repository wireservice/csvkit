#!/usr/bin/env python

import codecs
from collections import OrderedDict
import warnings

import agate
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
    ('unique', {
        'aggregation': None,
        'label': 'Unique values: '
    }),
    ('freq', {
        'aggregation': None,
        'label': 'Most common values: '
    }),
    ('len', {
        'aggregation': agate.MaxLength,
        'label': 'Longest value: '
    }),
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
        self.argparser.add_argument('--min', dest='min_only', action='store_true',
                                    help='Only output min.')
        self.argparser.add_argument('--max', dest='max_only', action='store_true',
                                    help='Only output max.')
        self.argparser.add_argument('--sum', dest='sum_only', action='store_true',
                                    help='Only output sum.')
        self.argparser.add_argument('--mean', dest='mean_only', action='store_true',
                                    help='Only output mean.')
        self.argparser.add_argument('--median', dest='median_only', action='store_true',
                                    help='Only output median.')
        self.argparser.add_argument('--stdev', dest='stdev_only', action='store_true',
                                    help='Only output standard deviation.')
        self.argparser.add_argument('--nulls', dest='nulls_only', action='store_true',
                                    help='Only output whether column contains nulls.')
        self.argparser.add_argument('--unique', dest='unique_only', action='store_true',
                                    help='Only output counts of unique values.')
        self.argparser.add_argument('--freq', dest='freq_only', action='store_true',
                                    help='Only output frequent values.')
        self.argparser.add_argument('--len', dest='len_only', action='store_true',
                                    help='Only output max value length.')
        self.argparser.add_argument('--count', dest='count_only', action='store_true',
                                    help='Only output row count')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        operations = [op for op in OPERATIONS.keys() if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one statistic argument may be specified (mean, median, etc).')

        if operations and self.args.count_only:
            self.argparser.error('You may not specify --count and a statistical argument at the same time.')

        if self.args.count_only:
            count = len(list(agate.csv.reader(self.input_file)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('Row count: %i\n' % count)

            return

        if six.PY2:
            self.output_file = codecs.getwriter('utf-8')(self.output_file)

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

                if op_name == 'type':
                    stat = column.data_type.__class__.__name__
                elif op_name == 'unique':
                    stat = len(column.values_distinct())
                elif op_name == 'freq':
                    stat = table.pivot(column_name).order_by('Count', reverse=True).limit(MAX_FREQ)
                else:
                    op = OPERATIONS[operations[0]]['aggregation']
                    stat = table.aggregate(op(column_name))

                # Formatting
                if op_name == 'freq':
                    stat = ', '.join([('"%s": %s' % (six.text_type(row[column_name]), row['Count'])) for row in stat])
                    stat = '{ %s }' % stat

                if len(table) == 1:
                    self.output_file.write(six.text_type(stat))
                else:
                    self.output_file.write('%3i. %s: %s\n' % (column_id + 1, column_name, stat))
            # Output all stats
            else:
                stats = {}

                label_column_width = 0
                value_column_width = 0
                freq_label_width = 0
                freq_value_width = 0

                for op_name, op_data in OPERATIONS.items():
                    label_column_width = max(label_column_width, len(op_data['label']))

                    if op_name == 'type':
                        stats[op_name] = '%ss' % column.data_type.__class__.__name__
                        continue
                    elif op_name == 'nulls':
                        if table.aggregate(agate.HasNulls(column_name)):
                            stats[op_name] = 'True (excluded from calculations)'
                        else:
                            stats[op_name] = 'False'
                        continue
                    elif op_name == 'unique':
                        stats[op_name] = len(column.values_distinct())
                        continue
                    elif op_name == 'freq':
                        stats[op_name] = table.pivot(column_name).order_by('Count', reverse=True).limit(MAX_FREQ)
                        continue

                    try:
                        op = op_data['aggregation']

                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', agate.NullCalculationWarning)
                            stats[op_name] = table.aggregate(op(column_name))
                    except:
                        stats[op_name] = None

                    if stats[op_name]:
                        value_column_width = max(value_column_width, len(str(stats[op_name])))

                # print(label_column_width)
                # print(value_column_width)
                # print(freq_label_width)
                # print(freq_value_width)

                self.output_file.write(('%3i. "%s"\n\n' % (column_id + 1, column_name)))

                for op_name, op_data in OPERATIONS.items():
                    if not stats[op_name]:
                        continue

                    if op_name == 'freq':
                        continue

                    label = '{label:{label_column_width}}'.format(**{
                        'label_column_width': label_column_width,
                        'label': op_data['label']
                    })

                    # value = '{value:{value_column_width}}'.format(**{
                    #     'value_column_width': value_column_width,
                    #     'value': stats[op_name]
                    # })

                    self.output_file.write('\t{} {}\n'.format(label, stats[op_name]))

                self.output_file.write('\n')

                # if stats['unique'] <= MAX_UNIQUE and not isinstance(column.data_type, agate.Boolean):
                #     uniques = [six.text_type(u) for u in column.values_distinct()]
                #     data = u'\tValues: %s\n' % ', '.join(uniques)
                #     self.output_file.write(data)
                # else:
                #     if isinstance(column.data_type, (agate.Number, agate.Date, agate.DateTime)):
                #         self.output_file.write('\tMinimum value: %s\n' % stats['min'])
                #         self.output_file.write('\tMaximum value: %s\n' % stats['max'])
                #
                #     if isinstance(column.data_type, agate.Number):
                #         self.output_file.write('\tSum: %s\n' % stats['sum'])
                #         self.output_file.write('\tMean: %s\n' % stats['mean'])
                #         self.output_file.write('\tMedian: %s\n' % stats['median'])
                #         self.output_file.write('\tStDev: %s\n' % stats['stdev'])
                #
                #     self.output_file.write('\tUnique values: %i\n' % stats['unique'])
                #
                # if isinstance(column.data_type, agate.Text):
                #     self.output_file.write('\tMax length: %i\n' % stats['len'])
                #
                # self.output_file.write('\tTop %i most common values:\n' % MAX_FREQ)
                #
                # for row in stats['freq']:
                #     self.output_file.write(('\t\t%s:\t%s\n' % (six.text_type(row[column_name]), row['Count'])))

        if not operations:
            self.output_file.write('Row count: %s\n' % len(table.rows))


def launch_new_instance():
    utility = CSVStat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
