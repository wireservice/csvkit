"""
The :class:`.Table` object is the most important class in agate. Tables are
created by supplying row data, column names and subclasses of :class:`.DataType`
to the constructor. Once created, the data in a table **can not be changed**.
This concept is central to agate.

Instead of modifying the data, various methods can be used to create new,
derivative tables. For example, the :meth:`.Table.select` method creates a new
table with only the specified columns. The :meth:`.Table.where` method creates
a new table with only those rows that pass a test. And :meth:`.Table.order_by`
creates a sorted table. In all of these cases the output is a new :class:`.Table`
and the existing table remains unmodified.

Tables are not themselves iterable, but the columns of the table can be
accessed via :attr:`.Table.columns` and the rows via :attr:`.Table.rows`. Both
sequences can be accessed either by numeric index or by name. (In the case of
rows, row names are optional.)
"""

import sys
import warnings
from io import StringIO
from itertools import chain

from agate import utils
from agate.columns import Column
from agate.data_types import DataType
from agate.exceptions import CastError
from agate.mapped_sequence import MappedSequence
from agate.rows import Row
from agate.type_tester import TypeTester


class Table:
    """
    A dataset consisting of rows and columns. Columns refer to "vertical" slices
    of data that must all be of the same type. Rows refer to "horizontal" slices
    of data that may (and usually do) contain mixed types.

    The sequence of :class:`.Column` instances are retrieved via the
    :attr:`.Table.columns` property. They may be accessed by either numeric
    index or by unique column name.

    The sequence of :class:`.Row` instances are retrieved via the
    :attr:`.Table.rows` property. They may be accessed by either numeric index
    or, if specified, unique row names.

    :param rows:
        The data as a sequence of any sequences: tuples, lists, etc. If
        any row has fewer values than the number of columns, it will be filled
        out with nulls. No row may have more values than the number of columns.
    :param column_names:
        A sequence of string names for each column or `None`, in which case
        column names will be automatically assigned using :func:`.letter_name`.
    :param column_types:
        A sequence of instances of :class:`.DataType` or an instance of
        :class:`.TypeTester` or `None` in which case a generic TypeTester will
        be used. Alternatively, a dictionary with column names as keys and
        instances of :class:`.DataType` as values to specify some types.
    :param row_names:
        Specifies unique names for each row. This parameter is
        optional. If specified it may be 1) the name of a single column that
        contains a unique identifier for each row, 2) a key function that takes
        a :class:`.Row` and returns a unique identifier or 3) a sequence of
        unique identifiers of the same length as the sequence of rows. The
        uniqueness of resulting identifiers is not validated, so be certain
        the values you provide are truly unique.
    :param _is_fork:
        Used internally to skip certain validation steps when data
        is propagated from an existing table. When :code:`True`, rows are
        assumed to be :class:`.Row` instances, rather than raw data.
    """
    def __init__(self, rows, column_names=None, column_types=None, row_names=None, _is_fork=False):
        if isinstance(rows, str):
            raise ValueError('When created directly, the first argument to Table must be a sequence of rows. '
                             'Did you want agate.Table.from_csv?')

        # Validate column names
        if column_names:
            self._column_names = utils.deduplicate(column_names, column_names=True)
        else:
            rows = iter(rows)
            try:
                first_row = next(rows)
            except StopIteration:
                self._column_names = tuple()
            else:
                rows = chain([first_row], rows)
                self._column_names = tuple(utils.letter_name(i) for i in range(len(first_row)))
                warnings.warn('Column names not specified. "%s" will be used as names.' % str(self._column_names),
                              RuntimeWarning, stacklevel=2)

        len_column_names = len(self._column_names)

        # Validate column_types
        if column_types is None:
            column_types = TypeTester()
        elif isinstance(column_types, dict):
            for v in column_types.values():
                if not isinstance(v, DataType):
                    raise ValueError('Column types must be instances of DataType.')

            column_types = TypeTester(force=column_types)
        elif not isinstance(column_types, TypeTester):
            for column_type in column_types:
                if not isinstance(column_type, DataType):
                    raise ValueError('Column types must be instances of DataType.')

        if isinstance(column_types, TypeTester):
            # Need to read all rows into memory.
            rows = tuple(rows)
            self._column_types = column_types.run(rows, self._column_names)
        else:
            self._column_types = tuple(column_types)

        if len_column_names != len(self._column_types):
            raise ValueError('column_names and column_types must be the same length.')

        if not _is_fork:
            new_rows = []
            cast_funcs = [c.cast for c in self._column_types]

            for i, row in enumerate(rows):
                len_row = len(row)

                if len_row > len_column_names:
                    raise ValueError(
                        'Row %i has %i values, but Table only has %i columns.' % (i, len_row, len_column_names)
                    )
                elif len(row) < len_column_names:
                    row = chain(row, [None] * (len_column_names - len_row))

                row_values = []
                for j, d in enumerate(row):
                    try:
                        row_values.append(cast_funcs[j](d))
                    except CastError as e:
                        raise CastError(str(e) + f' Error at row {i} column {self._column_names[j]}.')

                new_rows.append(Row(row_values, self._column_names))
        else:
            new_rows = rows

        if row_names:
            computed_row_names = []

            if isinstance(row_names, str):
                for row in new_rows:
                    name = row[row_names]
                    computed_row_names.append(name)
            elif hasattr(row_names, '__call__'):
                for row in new_rows:
                    name = row_names(row)
                    computed_row_names.append(name)
            elif utils.issequence(row_names):
                computed_row_names = row_names
            else:
                raise ValueError('row_names must be a column name, function or sequence')

            for row_name in computed_row_names:
                if type(row_name) is int:
                    raise ValueError('Row names cannot be of type int. Use Decimal for numbered row names.')

            self._row_names = tuple(computed_row_names)
        else:
            self._row_names = None

        self._rows = MappedSequence(new_rows, self._row_names)

        # Build columns
        new_columns = []

        for i in range(len_column_names):
            name = self._column_names[i]
            data_type = self._column_types[i]

            column = Column(i, name, data_type, self._rows, row_names=self._row_names)

            new_columns.append(column)

        self._columns = MappedSequence(new_columns, self._column_names)

    def __str__(self):
        """
        Print the table's structure using :meth:`.Table.print_structure`.
        """
        structure = StringIO()

        self.print_structure(output=structure)

        return structure.getvalue()

    def __len__(self):
        """
        Shorthand for :code:`len(table.rows)`.
        """
        return self._rows.__len__()

    def __iter__(self):
        """
        Shorthand for :code:`iter(table.rows)`.
        """
        return self._rows.__iter__()

    def __getitem__(self, key):
        """
        Shorthand for :code:`table.rows[foo]`.
        """
        return self._rows.__getitem__(key)

    @property
    def column_types(self):
        """
        An tuple :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        An tuple of strings.
        """
        return self._column_names

    @property
    def row_names(self):
        """
        An tuple of strings, if this table has row names.

        If this table does not have row names, then :code:`None`.
        """
        return self._row_names

    @property
    def columns(self):
        """
        A :class:`.MappedSequence` with column names for keys and
        :class:`.Column` instances for values.
        """
        return self._columns

    @property
    def rows(self):
        """
        A :class:`.MappedSeqeuence` with row names for keys (if specified) and
        :class:`.Row` instances for values.
        """
        return self._rows

    def _fork(self, rows, column_names=None, column_types=None, row_names=None):
        """
        Create a new table using the metadata from this one.

        This method is used internally by functions like
        :meth:`.Table.order_by`.

        :param rows:
            Row data for the forked table.
        :param column_names:
            Column names for the forked table. If not specified, fork will use
            this table's column names.
        :param column_types:
            Column types for the forked table. If not specified, fork will use
            this table's column names.
        :param row_names:
            Row names for the forked table. If not specified, fork will use
            this table's row names.
        """
        if column_names is None:
            column_names = self._column_names

        if column_types is None:
            column_types = self._column_types

        if row_names is None:
            row_names = self._row_names

        return Table(rows, column_names, column_types, row_names=row_names, _is_fork=True)

    def print_csv(self, **kwargs):
        """
        Print this table as a CSV.

        This is the same as passing :code:`sys.stdout` to :meth:`.Table.to_csv`.

        :code:`kwargs` will be passed on to :meth:`.Table.to_csv`.
        """
        self.to_csv(sys.stdout, **kwargs)

    def print_json(self, **kwargs):
        """
        Print this table as JSON.

        This is the same as passing :code:`sys.stdout` to
        :meth:`.Table.to_json`.

        :code:`kwargs` will be passed on to :meth:`.Table.to_json`.
        """
        self.to_json(sys.stdout, **kwargs)


from agate.table.aggregate import aggregate
from agate.table.bar_chart import bar_chart
from agate.table.bins import bins
from agate.table.column_chart import column_chart
from agate.table.compute import compute
from agate.table.denormalize import denormalize
from agate.table.distinct import distinct
from agate.table.exclude import exclude
from agate.table.find import find
from agate.table.from_csv import from_csv
from agate.table.from_fixed import from_fixed
from agate.table.from_json import from_json
from agate.table.from_object import from_object
from agate.table.group_by import group_by
from agate.table.homogenize import homogenize
from agate.table.join import join
from agate.table.limit import limit
from agate.table.line_chart import line_chart
from agate.table.merge import merge
from agate.table.normalize import normalize
from agate.table.order_by import order_by
from agate.table.pivot import pivot
from agate.table.print_bars import print_bars
from agate.table.print_html import print_html
from agate.table.print_structure import print_structure
from agate.table.print_table import print_table
from agate.table.rename import rename
from agate.table.scatterplot import scatterplot
from agate.table.select import select
from agate.table.to_csv import to_csv
from agate.table.to_json import to_json
from agate.table.where import where

Table.aggregate = aggregate
Table.bar_chart = bar_chart
Table.bins = bins
Table.column_chart = column_chart
Table.compute = compute
Table.denormalize = denormalize
Table.distinct = distinct
Table.exclude = exclude
Table.find = find
Table.from_csv = from_csv
Table.from_fixed = from_fixed
Table.from_json = from_json
Table.from_object = from_object
Table.group_by = group_by
Table.homogenize = homogenize
Table.join = join
Table.limit = limit
Table.line_chart = line_chart
Table.merge = merge
Table.normalize = normalize
Table.order_by = order_by
Table.pivot = pivot
Table.print_bars = print_bars
Table.print_html = print_html
Table.print_structure = print_structure
Table.print_table = print_table
Table.rename = rename
Table.scatterplot = scatterplot
Table.select = select
Table.to_csv = to_csv
Table.to_json = to_json
Table.where = where
