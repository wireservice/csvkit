#!/usr/bin/env python

import datetime
import math

from csvkit import table
from csvkit.cli import CSVKitUtility
from heapq import nlargest
from operator import itemgetter

class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = 'l'

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to be examined. Defaults to all columns.')
        self.argparser.add_argument('--max', dest='max_only', action='store_true',
                        help='Output will contain only max, unless there are multiple columns, in which case each value is prefixed with the column name')
        self.argparser.add_argument('--min', dest='min_only', action='store_true',
                        help='Output will contain only min, unless there are multiple columns, in which case each value is prefixed with the column name')
        self.argparser.add_argument('--sum', dest='sum_only', action='store_true',
                        help='Output will contain only sum, unless there are multiple columns, in which case each value is prefixed with the column name')
        self.argparser.add_argument('--mean', dest='mean_only', action='store_true',
                        help='Output will contain only mean, unless there are multiple columns, in which case each value is prefixed with the column name')
        self.argparser.add_argument('--median', dest='median_only', action='store_true',
                        help='Output will contain only median, unless there are multiple columns, in which case each value is prefixed with the column name')
        self.argparser.add_argument('--stdev', dest='stdev_only', action='store_true',
                        help='Output will contain only standard deviation, unless there are multiple columns, in which case each value is prefixed with the column name')

    def main(self):
        tab = table.Table.from_csv(self.args.file, snifflimit=self.args.snifflimit, column_ids=self.args.columns, **self.reader_kwargs)

        limit_keys = ('min', 'max', 'sum', 'mean', 'median', 'stdev')
        selected_keys = [k for k in limit_keys if getattr(self.args, k+'_only')]
        for c in tab:
            # WARNING: observe the correlation in naming against the argparse targets.
            maxval = minval = meanval = medialval = stdevval = None
            # Skip stats such as min/max for strings and bools
            # WARNING: observe the symmetry in the first two type checks with another block at the end.
            if c.type not in [unicode, bool] and c:
                values = sorted(filter(lambda i: i is not None, c))
                minval = min(values)
                maxval = max(values)
                if c.type in [int, float]:
                    sumval = sum(values)
                    meanval = float(sumval) / len(values)
                    medianval = median(values)
                    stdevval = math.sqrt(sum(math.pow(v-meanval, 2) for v in values) / len(values))
                if c.type in [datetime.datetime, datetime.date, datetime.time]:
                    minval = minval.isoformat()
                    maxval = maxval.isoformat()

            if selected_keys:
                # If multiple options are chosen, always choose the first selected option.
                val = locals()[selected_keys[0]+'val']
                self.output_file.write(u'%s%s' % (len(tab) != 1 and c.name+': ' or '', val and str(val)+'\n' or ''))
            else:
                uniques = set(c)
                uniques.discard(None)

                self.output_file.write((u'%3i. %s\n' % (c.order + 1, c.name)).encode('utf-8'))

                if c.type == None:
                    self.output_file.write(u'\tEmpty column\n')
                    continue
                    
                self.output_file.write(u'\t%s\n' % c.type)
                self.output_file.write(u'\tNulls: %s\n' % (u'Yes' if c.nullable else u'No'))
                
                if len(uniques) <= 5 and c.type is not bool:
                    uniques = [unicode(u) for u in list(uniques)]
                    self.output_file.write((u'\tValues: %s\n' % ', '.join(uniques)).encode('utf-8'))
                else:
                    # Skip stats such as min/max for strings and bools
                    # WARNING: observe the symmetry in the type checks with another block at the beginning.
                    if c.type not in [unicode, bool]:
                        self.output_file.write(u'\tMin: %s\n' % minval)
                        self.output_file.write(u'\tMax: %s\n' % maxval)
                        if c.type in [int, float]:
                            self.output_file.write(u'\tSum: %s\n' % sumval)
                            self.output_file.write(u'\tMean: %s\n' % meanval)
                            self.output_file.write(u'\tMedian: %s\n' % medianval)
                            self.output_file.write(u'\tStandard Deviation: %s\n' % stdevval)

                    self.output_file.write(u'\tUnique values: %i\n' % len(uniques))

                    if len(uniques) != len(values):
                        self.output_file.write(u'\t5 most frequent values:\n')
                        for value, count in freq(values):
                            self.output_file.write((u'\t\t%s:\t%s\n' % (unicode(value), count)).encode('utf-8'))

                    if c.type == unicode:
                        self.output_file.write(u'\tMax length: %i\n' % c.max_length)

        if not selected_keys:
            self.output_file.write(u'\n')
            self.output_file.write(u'Row count: %s\n' % tab.count_rows())

def median(l):
    """
    compute the median of a list.
    """
    length = len(l)

    if len(l) % 2 == 1:
        return l[((length + 1) / 2) - 1]
    else:
        a = l[(length / 2) - 1]
        b = l[length / 2]
    return (float(a + b)) / 2  

def freq(l):
    """
    Count the number of times each value occurs in a column.
    """
    count = {}
    n = 5

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
