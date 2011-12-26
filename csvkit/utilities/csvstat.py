#!/usr/bin/env python

import datetime
from types import NoneType
import math

from csvkit import table
from csvkit.cli import CSVKitUtility
from heapq import nlargest
from operator import itemgetter

MAX_UNIQUE = 5
MAX_FREQ = 5
OPERATIONS =('min', 'max', 'sum', 'mean', 'median', 'stdev', 'nulls', 'unique', 'freq', 'len')

class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = 'l'

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes.')
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

    def main(self):
        tab = table.Table.from_csv(self.args.file, snifflimit=self.args.snifflimit, column_ids=self.args.columns, **self.reader_kwargs)

        operations = [op for op in OPERATIONS if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one statistic argument may be specified (mean, median, etc).')

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
                    stat = ', '.join([(u'"%s": %s' % (unicode(k), count)).encode('utf-8') for k, count in stat])
                    stat = '{ %s }' % stat

                if len(tab) == 1:
                    self.output_file.write(unicode(stat))
                else:
                    self.output_file.write(u'%3i. %s: %s\n' % (c.order + 1, c.name, stat))
            # Output all stats
            else:
                for op in OPERATIONS:
                    stats[op] = getattr(self, 'get_%s' % op)(c, values, stats)

                self.output_file.write((u'%3i. %s\n' % (c.order + 1, c.name)).encode('utf-8'))

                if c.type == None:
                    self.output_file.write(u'\tEmpty column\n')
                    continue
                    
                self.output_file.write(u'\t%s\n' % c.type)
                self.output_file.write(u'\tNulls: %s\n' % stats['nulls'])
                
                if len(stats['unique']) <= MAX_UNIQUE and c.type is not bool:
                    uniques = [unicode(u) for u in list(stats['unique'])]
                    self.output_file.write((u'\tValues: %s\n' % u', '.join(uniques)).encode('utf-8'))
                else:
                    if c.type not in [unicode, bool]:
                        self.output_file.write(u'\tMin: %s\n' % stats['min'])
                        self.output_file.write(u'\tMax: %s\n' % stats['max'])

                        if c.type in [int, float]:
                            self.output_file.write(u'\tSum: %s\n' % stats['sum'])
                            self.output_file.write(u'\tMean: %s\n' % stats['mean'])
                            self.output_file.write(u'\tMedian: %s\n' % stats['median'])
                            self.output_file.write(u'\tStandard Deviation: %s\n' % stats['stdev'])

                    self.output_file.write(u'\tUnique values: %i\n' % len(stats['unique']))

                    if len(stats['unique']) != len(values):
                        self.output_file.write(u'\t%i most frequent values:\n' % MAX_FREQ)
                        for value, count in stats['freq']:
                            self.output_file.write((u'\t\t%s:\t%s\n' % (unicode(value), count)).encode('utf-8'))

                    if c.type == unicode:
                        self.output_file.write(u'\tMax length: %i\n' % stats['len'])

        if not operations:
            self.output_file.write(u'\n')
            self.output_file.write(u'Row count: %s\n' % tab.count_rows())

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
        if c.type != unicode:
            return None

        return c.max_length()

def median(l):
    """
    Compute the median of a list.
    """
    length = len(l)

    if len(l) % 2 == 1:
        return l[((length + 1) / 2) - 1]
    else:
        a = l[(length / 2) - 1]
        b = l[length / 2]
    return (float(a + b)) / 2  

def freq(l, n=MAX_FREQ):
    """
    Count the number of times each value occurs in a column.
    """
    count = {}

    for x in l:
        s = unicode(x)
        if count.has_key(s):
            count[s] += 1
        else:
            count[s] = 1

    # This will iterate through dictionary, return N highest
    # values as (key, value) tuples.
    top = nlargest(n, count.iteritems(), itemgetter(1))

    return top

if __name__ == '__main__':
    utility = CSVStat()
    utility.main()

