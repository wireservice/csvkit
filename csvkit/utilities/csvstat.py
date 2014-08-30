#!/usr/bin/env python

import datetime
from heapq import nlargest
from operator import itemgetter
import math

import six

from csvkit import CSVKitReader, table
from csvkit.cli import CSVKitUtility

NoneType = type(None)

MAX_UNIQUE = 5
MAX_FREQ = 5
OPERATIONS =('min', 'max', 'sum', 'mean', 'median', 'stdev', 'nulls', 'unique', 'freq', 'len')

class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = ['l']

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
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
            help='Only output unique values.')
        self.argparser.add_argument('--freq', dest='freq_only', action='store_true',
            help='Only output frequent values.')
        self.argparser.add_argument('--len', dest='len_only', action='store_true',
            help='Only output max value length.')
        self.argparser.add_argument('--count', dest='count_only', action='store_true',
            help='Only output row count')

    def main(self):
        operations = [op for op in OPERATIONS if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one statistic argument may be specified (mean, median, etc).')

        if operations and self.args.count_only:
            self.argparser.error('You may not specify --count and a statistical argument at the same time.')

        if self.args.count_only:
            count = len(list(CSVKitReader(self.input_file)))

            if not self.args.no_header_row:
                count -= 1
            
            self.output_file.write('Row count: %i\n' % count)

            return

        tab = table.Table.from_csv(
            self.input_file,
            snifflimit=self.args.snifflimit,
            column_ids=self.args.columns,
            zero_based=self.args.zero_based,
            no_header_row=self.args.no_header_row,
            **self.reader_kwargs
        )

        for c in tab:
            values = sorted(filter(lambda i: i is not None, c))

            stats = {} 

            # Output a single stat
            if len(operations) == 1:
                op = operations[0]
                stat = getattr(self, 'get_%s' % op)(c, values, {})

                # Formatting
                if op == 'unique':
                    stat = len(stat)
                elif op == 'freq':
                    stat = ', '.join([('"%s": %s' % (six.text_type(k), count)) for k, count in stat])
                    stat = '{ %s }' % stat

                if len(tab) == 1:
                    self.output_file.write(six.text_type(stat))
                else:
                    self.output_file.write('%3i. %s: %s\n' % (c.order + 1, c.name, stat))
            # Output all stats
            else:
                for op in OPERATIONS:
                    stats[op] = getattr(self, 'get_%s' % op)(c, values, stats)

                self.output_file.write(('%3i. %s\n' % (c.order + 1, c.name)))

                if c.type == None:
                    self.output_file.write('\tEmpty column\n')
                    continue
                    
                self.output_file.write('\t%s\n' % c.type)
                self.output_file.write('\tNulls: %s\n' % stats['nulls'])
                
                if len(stats['unique']) <= MAX_UNIQUE and c.type is not bool:
                    uniques = [six.text_type(u) for u in list(stats['unique'])]
                    data = u'\tValues: %s\n' % ', '.join(uniques)
                    self.output_file.write(data)
                else:
                    if c.type not in [six.text_type, bool]:
                        self.output_file.write('\tMin: %s\n' % stats['min'])
                        self.output_file.write('\tMax: %s\n' % stats['max'])

                        if c.type in [int, float]:
                            self.output_file.write('\tSum: %s\n' % stats['sum'])
                            self.output_file.write('\tMean: %s\n' % stats['mean'])
                            self.output_file.write('\tMedian: %s\n' % stats['median'])
                            self.output_file.write('\tStandard Deviation: %s\n' % stats['stdev'])

                    self.output_file.write('\tUnique values: %i\n' % len(stats['unique']))

                    if len(stats['unique']) != len(values):
                        self.output_file.write('\t%i most frequent values:\n' % MAX_FREQ)
                        for value, count in stats['freq']:
                            self.output_file.write(('\t\t%s:\t%s\n' % (six.text_type(value), count)))

                    if c.type == six.text_type:
                        self.output_file.write('\tMax length: %i\n' % stats['len'])

        if not operations:
            self.output_file.write('\n')
            self.output_file.write('Row count: %s\n' % tab.count_rows())

    def get_min(self, c, values, stats):
        if c.type == NoneType:
            return None

        v = min(values)

        if v in [datetime.datetime, datetime.date, datetime.time]:
            return v.isoformat()
        
        return v

    def get_max(self, c, values, stats):
        if c.type == NoneType:
            return None

        v = max(values)

        if v in [datetime.datetime, datetime.date, datetime.time]:
            return v.isoformat()
        
        return v

    def get_sum(self, c, values, stats):
        if c.type not in [int, float]:
            return None

        return sum(values)

    def get_mean(self, c, values, stats):
        if c.type not in [int, float]:
            return None

        if 'sum' not in stats:
            stats['sum'] = self.get_sum(c, values, stats)

        return float(stats['sum']) / len(values)

    def get_median(self, c, values, stats):
        if c.type not in [int, float]:
            return None

        return median(values)

    def get_stdev(self, c, values, stats):
        if c.type not in [int, float]:
            return None

        if 'mean' not in stats:
            stats['mean'] = self.get_mean(c, values, stats)

        return math.sqrt(sum(math.pow(v - stats['mean'], 2) for v in values) / len(values)) 

    def get_nulls(self, c, values, stats):
        return c.has_nulls()

    def get_unique(self, c, values, stats):
        return set(values) 

    def get_freq(self, c, values, stats):
        return freq(values) 

    def get_len(self, c, values, stats):
        if c.type != six.text_type:
            return None

        return c.max_length()

def median(l):
    """
    Compute the median of a list.
    """
    length = len(l)

    if length % 2 == 1:
        return l[(length + 1) // 2 - 1]
    else:
        a = l[(length // 2) - 1]
        b = l[length // 2]
    return (float(a + b)) / 2  

def freq(l, n=MAX_FREQ):
    """
    Count the number of times each value occurs in a column.
    """
    count = {}

    for x in l:
        s = six.text_type(x)

        if s in count:
            count[s] += 1
        else:
            count[s] = 1

    # This will iterate through dictionary, return N highest
    # values as (key, value) tuples.
    top = nlargest(n, six.iteritems(count), itemgetter(1))

    return top


def launch_new_instance():
    utility = CSVStat()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

