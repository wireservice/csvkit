#!/usr/bin/env python

import datetime

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

    def main(self):
        tab = table.Table.from_csv(self.args.file, snifflimit=self.args.snifflimit, column_ids=self.args.columns, **self.reader_kwargs)

        for c in tab:
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
                values = sorted(filter(lambda i: i is not None, c))
                
                # Skip min/max for strings and bools
                if c.type not in [unicode, bool]:
                    minval = min(values)
                    maxval = max(values)

                    if c.type in [datetime.datetime, datetime.date, datetime.time]:
                        minval = minval.isoformat()
                        maxval = maxval.isoformat()

                    self.output_file.write(u'\tMin: %s\n' % min(values))
                    self.output_file.write(u'\tMax: %s\n' % max(values))

                    if c.type in [int, float]:
                        self.output_file.write(u'\tSum: %s\n' % sum(values))
                        self.output_file.write(u'\tMean: %s\n' % (sum(values) / len(values)))
                        self.output_file.write(u'\tMedian: %s\n' % median(values))

                self.output_file.write(u'\tUnique values: %i\n' % len(uniques))

                if len(uniques) != len(values):
                    self.output_file.write(u'\t5 most frequent values:\n')
                    for value, count in freq(values):
                        self.output_file.write((u'\t\t%s:\t%s\n' % (unicode(value), count)).encode('utf-8'))

                if c.type == unicode:
                    self.output_file.write(u'\tMax length: %i\n' % c.max_length)

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
