#!/usr/bin/env python

import datetime
from cStringIO import StringIO

from csvkit import CSVKitReader, CSVKitWriter
from csvkit import sniffer
from csvkit import typeinference

class InvalidType(object):
    """
    Dummy object type for Column initialization, since None is being used as a valid value.
    """
    pass

class Column(list):
    """
    A normalized data column and inferred annotations (nullable, etc.).
    """
    def __init__(self, order, name, l, normal_type=InvalidType):
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
        self.order = order
        self.name = name or '_unnamed' # empty column names don't make sense 
        self.type = t
        
        self._compute_nullable() 
        self._compute_max_length()

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        """
        Stringify a description of this column.
        """
        return '%3i: %s (%s)' % (self.order, self.name, self.type)

    def __getitem__(self, key):
        """
        Return null for keys beyond the range of the column. This allows for columns to be of uneven length and still be merged into rows cleanly.
        """
        if key >= len(self):
            return None

        return list.__getitem__(self, key)

    def _compute_nullable(self):
        self.nullable = True if None in self else False

    def _compute_max_length(self):
        """
        Compute maximum length this column occupies when rendered as a string.
        """
        if len(self) == 0:
            self.max_length = 0
            return

        if self.type == unicode:
            self.max_length = max([len(d) if d else 0 for d in self])
        elif self.type in [int, float]:
            self.max_length = max([len(unicode(d)) if d else 0 for d in self])
        elif self.type in [datetime.datetime, datetime.date, datetime.time]:
            self.max_length = max([len(d.isoformat()) if d else 0 for d in self]) 
        elif self.type == bool:
            self.max_length = 5 # "False"
        else:
            self.max_length = 0 

        if self.nullable:
            self.max_length = max(self.max_length, 4) # "None"

class Table(list):
    """
    A normalized data table and inferred annotations (nullable, etc.).
    """
    def __init__(self, columns=[], name='new_table'):
        """
        Generic constructor. You should normally use a from_* method to create a Table.
        """
        list.__init__(self, columns)
        self.name = name

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        """
        Stringify a description of all columns in this table.
        """
        return '\n'.join([unicode(c) for c in self])

    def _reindex_columns(self):
        """
        Update order properties of all columns in table.
        """
        for i, c in enumerate(self):
            c.order = i

    def _deduplicate_column_name(self, column):
        while column.name in self.headers():
            try:
                i = column.name.rindex('_')
                counter = int(column.name[i + 1:])
                column.name = '%s_%i' % (column.name[:i], counter + 1)
            except:
                column.name += '_2'

        return column.name

    def append(self, column):
        """Implements list append."""
        self._deduplicate_column_name(column)

        list.append(self, column)
        column.index = len(self) - 1

    def insert(self, i, column):
        """Implements list insert."""
        self._deduplicate_column_name(column)

        list.insert(self, i, column)
        self._reindex_columns()

    def extend(self, columns):
        """Implements list extend."""
        for c in columns:
            self._deduplicate_column_name(c)

        list.extend(self, columns)
        self._reindex_columns()

    def remove(self, column):
        """Implements list remove."""
        list.remove(self, column)
        self._reindex_columns()

    def sort(self):
        """Forbids list sort."""
        raise NotImplementedError()

    def reverse(self):
        """Forbids list reverse."""
        raise NotImplementedError()

    def headers(self):
        return [c.name for c in self]

    def count_rows(self):
        lengths = [len(c) for c in self]

        if lengths:
            return max(lengths)

        return 0

    def row(self, i):
        """
        Fetch a row of data from this table.
        """
        if i < 0:
            raise IndexError('Negative row numbers are not valid.')

        if i >= self.count_rows():
            raise IndexError('Row number exceeds the number of rows in the table.')

        row_data = [c[i] for c in self]

        return row_data

    @classmethod
    def from_csv(cls, f, name='from_csv_table', **kwargs):
        """
        Creates a new Table from a file-like object containing CSV data.
        """
        # This bit of nonsense is to deal with "files" from stdin,
        # which are not seekable and thus must be buffered
        contents = f.read()

        sample = contents
        dialect = sniffer.sniff_dialect(sample)

        f = StringIO(contents) 
        reader = CSVKitReader(f, dialect=dialect, **kwargs)

        headers = reader.next()

        data_columns = [[] for c in headers] 

        for row in reader:
            for i, d in enumerate(row):
                try:
                    data_columns[i].append(d.strip())
                except IndexError:
                    # Non-rectangular data is truncated
                    break

        columns = []

        for i, c in enumerate(data_columns): 
            columns.append(Column(i, headers[i], c))

        return Table(columns, name=name)

    def to_rows(self, serialize_dates=False):
        """
        Generates rows from columns and performs.

        Optionally serialize date objects to isoformat strings.
        """
        if serialize_dates:
            out_columns = []

            for c in self:
                # Stringify datetimes, dates, and times
                if c.type in [datetime.datetime, datetime.date, datetime.time]:
                    out_columns.append([unicode(v.isoformat()) if v != None else None for v in c])
                else:
                    out_columns.append(c)

            # Convert columns to rows 
            return zip(*out_columns)
        else:
            return zip(*self)

    def to_csv(self, output, **kwargs):
        """
        Serializes the table to CSV and writes it to any file-like object.
        """
        rows = self.to_rows(serialize_dates=True)

        # Insert header row
        rows.insert(0, self.headers())

        writer = CSVKitWriter(output, **kwargs)
        writer.writerows(rows)
