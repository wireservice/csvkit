#!/usr/bin/env python

import datetime

from csvkit import typeinference
from csvkit.unicode import UnicodeCSVReader, UnicodeCSVWriter

class InvalidType(object):
    """
    Dummy object type for Column initialization, since None is being used as a valid value.
    """
    pass

class Column(list):
    """
    A normalized data column and inferred annotations (nullable, etc.).
    """
    def __init__(self, index, name, l, normal_type=InvalidType):
        """
        Construct a column from a sequence of values.
        
        If normal_type is not None, inference will be skipped and values assumed to have already been normalized.
        """
        if normal_type != InvalidType:
            t = normal_type
            data = l
        else:
            t, data = typeinference.normalize_column_type(l)
        
        list.__init__(self, data)
        self.index = index
        self.name = name 
        self.type = t
        # self.nullable = ?
        # self.max_length = ?

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        """
        Stringify a description of this column.
        """
        return '%3i: %s (%s)' % (self.index, self.name, self.type)

class RowIterator(object):
    """
    An iterator which constructs rows from a Table each time one is requested.
    """
    def __init__(self, table):
		self.table = table
		self.i = 0

    def __iter__(self):
        return self

    def next(self):
        if self.i == self.table.row_count:
            raise StopIteration
        else:
            row = self.table.row(self.i)
            self.i += 1
            return row

class Table(list):
    """
    A normalized data table and inferred annotations (nullable, etc.).
    """
    def __init__(self, columns=[]):
        """
        Generic constructor. You should normally use a from_* method to create a Table.
        """
        list.__init__(self, columns)
        self._update_row_count()

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        """
        Stringify a description of all columns in this table.
        """
        return '\n'.join([unicode(c) for c in self])

    def _reindex_columns(self):
        """
        Update index properties of all columns in table.
        """
        for i, c in enumerate(self):
            c.index = i

    def _update_row_count(self):
        """
        Update the row count.
        """
        if self:
            self.row_count = max([len(c) for c in self])
        else:
            self.row_count = 0

    def append(self, column):
        """Implements list append."""
        list.append(self, column)
        column.index = len(self) - 1

        if len(column) > self.row_count:
            self.row_count = len(column)

    def insert(self, i, column):
        """Implements list insert."""
        list.insert(self, i, column)
        self._reindex_columns()

        if len(column) > self.row_count:
            self.row_count = len(column)

    def extend(self, columns):
        """Implements list extend."""
        list.extend(self, columns)
        self._reindex_columns()

        self._update_row_count()

    def remove(self, column):
        """Implements list remove."""
        list.remove(self, column)
        self._reindex_columns()

        self._update_row_count()

    def sort(self):
        """Forbids list sort."""
        raise NotImplementedError()

    def reverse(self):
        """Forbids list reverse."""
        raise NotImplementedError()

    def headers(self):
        return [c.name for c in self]

    def row(self, i):
        """
        Fetch a row of data from this table.
        """
        return [c[i] for c in self]

    def rows(self):
        """
        Iterate over the rows in this table.
        """
        return RowIterator(self)

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

        return Table(columns)

    def to_csv(self, output, skipheader=False, **kwargs):
        """
        Serializes the table to CSV and writes it to any file-like object.
        """
        out_columns = []
        
        for c in self:
            # Stringify datetimes, dates, and times
            if c.type in [datetime.datetime, datetime.date, datetime.time]:
                out_columns.append([v.isoformat() if v != None else None for v in c])
            else:
                out_columns.append(c)
        
        # Convert columns to rows
        rows = zip(*out_columns)

        # Insert header row
        if not skipheader:
            rows.insert(0, [c.name for c in self])

        writer_kwargs = { 'lineterminator': '\n' }
        writer_kwargs.update(kwargs)

        writer = UnicodeCSVWriter(output, **writer_kwargs)
        writer.writerows(rows)
