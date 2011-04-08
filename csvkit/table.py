#!/usr/bin/env python

import datetime

from csvkit import typeinference
from csvkit.unicode import UnicodeCSVReader, UnicodeCSVWriter

class Column(list):
    """
    A normalized data column and inferred annotations (nullable, etc.).
    """
    def __init__(self, index, name, l):
        """
        Construct a column from a sequence of values.
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
        """
        Stringify a description of this column.
        """
        return '%3i: %s (%s)' (self.index, self.name, self.type)

class Table(object):
    """
    A normalized data table and inferred annotations (nullable, etc.).
    """
    def __init__(self, headers, columns):
        """
        Generic constructor. You should normally use a from_* method to create a Table.
        """
        self.headers = headers 
        self.columns = columns

    def __unicode__(self):
        """
        Stringify a description of all columns in this table.
        """
        return '\n'.join([unicode(c) for c in self.columns])

    @classmethod
    def from_csv(self, f, **kwargs):
        """
        Creates a new Table from a file-like object containng CSV data.
        """
        reader = UnicodeCSVReader(f, **kwargs)

        headers = reader.next()

        # Data is processed first into columns (rather than rows) for easier type inference
        data_columns = [[] for c in headers] 

        for row in reader:
            for i, d in enumerate(row):
                try:
                    data_columns[i].append(d.strip())
                except KeyError:
                    # Non-rectangular data is truncated
                    break

        columns = []

        # Convert to "heavy" columns
        for i, c in enumerate(data_columns): 
            columns.append(Column(i, headers[i], c))

        return Table(headers, columns)

    def to_csv(self, output, **kwargs):
        """
        Serializes the table to CSV and writes it to any file-like object.
        """
        out_columns = []
        
        for c in self.columns:
            # Stringify datetimes, dates, and times
            if c.type in [datetime.datetime, datetime.date, datetime.time]:
                out_columns.append([v.isoformat() if v != None else None for v in c])
            else:
                out_columns.append(c)
        
        # Convert columns to rows
        rows = zip(*out_columns)

        # Insert header row
        rows.insert(0, self.headers)

        writer_kwargs = { 'lineterminator': '\n' }
        writer_kwargs.update(kwargs)

        writer = UnicodeCSVWriter(output, **writer_kwargs)
        writer.writerows(rows)
