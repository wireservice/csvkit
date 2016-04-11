#!/usr/bin/env python

import csv
import datetime
import itertools

import agate
import six

from csvkit import typeinference
from csvkit.cli import parse_column_identifiers, make_default_headers

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']


def sniff_dialect(sample):
    """
    A functional version of ``csv.Sniffer().sniff``, that extends the
    list of possible delimiters to include some seen in the wild.
    """
    try:
        dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
    except:
        dialect = None

    return dialect


class InvalidType(object):
    """
    Dummy object type for Column initialization, since None is being used as a valid value.
    """
    pass


class Column(list):
    """
    A normalized data column and inferred annotations (nullable, etc.).
    """

    def __init__(self, order, name, l, normal_type=InvalidType, blanks_as_nulls=True, infer_types=True):
        """
        Construct a column from a sequence of values.

        If normal_type is not InvalidType, inference will be skipped and values assumed to have already been normalized.
        If infer_types is False, type inference will be skipped and the type assumed to be unicode.
        """
        if normal_type != InvalidType:
            t = normal_type
            data = l
        elif not infer_types:
            t = six.text_type
            data = l
        else:
            t, data = typeinference.normalize_column_type(l, blanks_as_nulls=blanks_as_nulls)

        list.__init__(self, data)
        self.order = order
        self.name = name or '_unnamed'  # empty column names don't make sense
        self.type = t

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
        l = len(self)

        if isinstance(key, slice):
            indices = six.moves.range(*key.indices(l))
            return [(list.__getitem__(self, i) if i < l else None) for i in indices]

        if key >= l:
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

        if self.type == six.text_type:
            l = max(len(d) if d else 0 for d in self)

            if self.has_nulls():
                l = max(l, 4)  # "None"

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

    def headers(self):
        return [c.name for c in self]

    def count_rows(self):
        lengths = [len(c) for c in self]

        if lengths:
            return max(lengths)

        return 0

    @classmethod
    def from_csv(cls, f, name='from_csv_table', sniff_limit=None, column_ids=None, blanks_as_nulls=True, column_offset=1, infer_types=True, no_header_row=False, **kwargs):
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

        # sniff_limit == 0 means do not sniff
        if sniff_limit is None:
            kwargs['dialect'] = sniff_dialect(contents)
        elif sniff_limit > 0:
            kwargs['dialect'] = sniff_dialect(contents[:sniff_limit])

        f = six.StringIO(contents)
        rows = agate.csv.reader(f, **kwargs)

        try:
            if no_header_row:
                # Peek at a row to infer column names from, and put it back on top
                row = next(rows)
                rows = itertools.chain([row], rows)
                headers = make_default_headers(len(row))
            else:
                headers = next(rows)
        except StopIteration:
            # The file is `/dev/null`.
            headers = []
            pass

        if no_header_row or column_ids:
            column_ids = parse_column_identifiers(column_ids, headers, column_offset)
            headers = [headers[c] for c in column_ids]
        else:
            column_ids = range(len(headers))

        data_columns = [[] for c in headers]
        width = len(data_columns)

        for i, row in enumerate(rows):
            j = 0

            for j, d in enumerate(row):
                try:
                    data_columns[j].append(row[column_ids[j]].strip())
                except IndexError:
                    # Non-rectangular data is truncated
                    break

            j += 1

            # Populate remaining columns with None
            while j < width:
                data_columns[j].append(None)

                j += 1

        columns = []

        for i, c in enumerate(data_columns):
            columns.append(Column(column_ids[i], headers[i], c, blanks_as_nulls=blanks_as_nulls, infer_types=infer_types))

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
                    out_columns.append([six.text_type(v.isoformat()) if v is not None else None for v in c])
                else:
                    out_columns.append(c)

            # Convert columns to rows
            return list(zip(*out_columns))
        else:
            return list(zip(*self))
