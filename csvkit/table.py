#!/usr/bin/env python

from cStringIO import StringIO

from csvkit import typeinference
from csvkit.unicode import UnicodeCSVReader, UnicodeCSVWriter

class Column(list):
    """
    A normalized data column and inferred annotations (nullable, etc.).
    """
    def __init__(self, index, name, l):
        """
        Construct a column from a sequence of values.

        TODO: anything special for iterators?
        """
        t, data = typeinference.normalize_column_type(l)
        
        list.__init__(self, data)
        self.index = index
        self.name = name 
        self.type = t
        # self.nullable = ?
        # self.max_length = ?

    def __getslice__(self, i, j):
        return list.__getslice__(self, i, j)

    def __unicode__(self):
        return '%3i: %s (%s)' (self.index, self.name, self.type)

class Table(object):
    """
    A normalized data table and inferred annotations (nullable, etc.).
    """
    def __init__(self, f, **kwargs):
        """
        Construct a table from an csv.reader or reader-like iterable.
        """
        reader = UnicodeCSVReader(f, **kwargs)

        self.headers = reader.next()

        # Data is processed first into columns (rather than rows) for easier type inference
        data_columns = [[] for c in self.headers] 

        for row in reader:
            for i, d in enumerate(row):
                try:
                    data_columns[i].append(d.strip())
                except KeyError:
                    # Non-rectangular data is truncated
                    break

        # Convert to "heavy" columns
        self.columns = [Column(n, c) for n, c in zip(self.headers, data_columns)]

    def __unicode__(self):
        return '\n'.join([unicode(c) for c in self.columns])

    def to_csv(self):
        """
        Serializes the table to a CSV string.
        """
        # Convert columns to rows
        data = zip(*data_columns)

        # Insert header row
        data.insert(0, headers)

        # Stringify datetimes, dates, and times
        if t in [datetime.datetime, datetime.date, datetime.time]:
            column = [v.isoformat() if v != None else None for v in column]

        o = StringIO()
        writer = UnicodeCSVWriter(o, lineterminator='\n')
        writer.writerows(rows)
        output = o.getvalue()
        o.close()

        return output
