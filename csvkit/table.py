#!/usr/bin/env python

import datetime
from cStringIO import StringIO

from csvkit import CSVKitReader, CSVKitWriter
from csvkit import sniffer
from csvkit import typeinference
from csvkit.cli import parse_column_identifiers

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
        
        If normal_type is not InvalidType, inference will be skipped and values assumed to have already been normalized.
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
        
    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        """
        Stringify a description of this column.
        """
        return u'%3i: %s (%s)' % (self.order, self.name, self.type)

    def __getitem__(self, key):
        """
        Return null for keys beyond the range of the column. This allows for columns to be of uneven length and still be merged into rows cleanly.
        """
        if key >= len(self):
            return None

        return list.__getitem__(self, key)

    def has_nulls(self):
        """
        Check if this column contains nulls.
        """
        return True if None in self else False

    def max_length(self):
        """
        Compute maximum length of data in this column.
        
        Returns 0 if the column does not of type ``unicode``.
        """
        l = 0

        if self.type == unicode:
            l = max([len(d) if d else 0 for d in self])

            if self.has_nulls():
                l = max(l, 4) # "None"

        return l

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
        return u'\n'.join([unicode(c) for c in self])

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
    def from_csv(cls, f, name='from_csv_table', snifflimit=None, column_ids=None, **kwargs):
        """
        Creates a new Table from a file-like object containing CSV data.

        Note: the column_ids argument will cause only those columns with a matching identifier
        to be parsed, type inferred, etc. However, their order/index property will reflect the
        original data (e.g. column 8 will still be "order" 7, even if it's the third column
        in the resulting Table.
        """
        # This bit of nonsense is to deal with "files" from stdin,
        # which are not seekable and thus must be buffered
        contents = f.read()

        if snifflimit:
            sample = contents[:snifflimit]
        else:
            sample = contents

        dialect = sniffer.sniff_dialect(sample)

        f = StringIO(contents) 
        reader = CSVKitReader(f, dialect=dialect, **kwargs)

        headers = reader.next()
        
        if column_ids:
            column_ids = parse_column_identifiers(column_ids, headers)
            headers = [headers[c] for c in column_ids]
        else:
            column_ids = range(len(headers))
        
        data_columns = [[] for c in headers]

        for row in reader:
            for i, d in enumerate(row):
                try:
                    data_columns[i].append(row[column_ids[i]].strip())
                except IndexError:
                    # Non-rectangular data is truncated
                    break

        columns = []

        for i, c in enumerate(data_columns):
            columns.append(Column(column_ids[i], headers[i], c))

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

