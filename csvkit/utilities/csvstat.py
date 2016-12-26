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
    ('min', agate.Min),
    ('max', agate.Max),
    ('sum', agate.Sum),
    ('mean', agate.Mean),
    ('median', agate.Median),
    ('stdev', agate.StDev),
    ('nulls', agate.HasNulls),
    ('unique', None),
    ('freq', None),
    ('len', agate.MaxLength)
])


class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = ['l']

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices or names to be examined. Defaults to all columns.')
        self.argparser.add_argument('--max', dest='max_only', action='store_true',
                                    help='Only output max.')
        self.argparser.add_argument('--min', dest='min_only', action='store_true',
                                    help='Only output min.')
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

                if op_name == 'unique':
                    stat = len(column.values_distinct())
                elif op_name == 'freq':
                    stat = table.pivot(column_name).order_by('Count', reverse=True).limit(MAX_FREQ)
                else:
                    op = OPERATIONS[operations[0]]
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

                for op_name, op in OPERATIONS.items():
                    if op_name == 'unique':
                        stats[op_name] = len(column.values_distinct())
                        continue
                    elif op_name == 'freq':
                        stats[op_name] = table.pivot(column_name).order_by('Count', reverse=True).limit(MAX_FREQ)
                        continue

                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', agate.NullCalculationWarning)
                            stats[op_name] = table.aggregate(op(column_name))
                    except:
                        stats[op_name] = None

                self.output_file.write(('%3i. %s\n' % (column_id + 1, column_name)))

                self.output_file.write('\tType of data: %ss\n' % column.data_type.__class__.__name__)

                if stats['nulls']:
                    self.output_file.write('\tContains null values: True (excluded from calculations)\n')
                else:
                    self.output_file.write('\tContains values: False\n')

                if stats['unique'] <= MAX_UNIQUE and not isinstance(column.data_type, agate.Boolean):
                    uniques = [six.text_type(u) for u in column.values_distinct()]
                    data = u'\tValues: %s\n' % ', '.join(uniques)
                    self.output_file.write(data)
                else:
                    if isinstance(column.data_type, (agate.Number, agate.Date, agate.DateTime)):
                        self.output_file.write('\tMinimum value: %s\n' % stats['min'])
                        self.output_file.write('\tMaximum value: %s\n' % stats['max'])

                    if isinstance(column.data_type, agate.Number):
                        self.output_file.write('\tSum: %s\n' % stats['sum'])
                        self.output_file.write('\tMean: %s\n' % stats['mean'])
                        self.output_file.write('\tMedian: %s\n' % stats['median'])
                        self.output_file.write('\tStDev: %s\n' % stats['stdev'])

                    self.output_file.write('\tUnique values: %i\n' % stats['unique'])

                if isinstance(column.data_type, agate.Text):
                    self.output_file.write('\tMax length: %i\n' % stats['len'])

                self.output_file.write('\tTop %i most common values:\n' % MAX_FREQ)

                for row in stats['freq']:
                    self.output_file.write(('\t\t%s:\t%s\n' % (six.text_type(row[column_name]), row['Count'])))

        if not operations:
            self.output_file.write('\n')
            self.output_file.write('Row count: %s\n' % len(table.rows))


def launch_new_instance():
    utility = CSVStat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
