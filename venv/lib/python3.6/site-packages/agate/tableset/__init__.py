"""
The :class:`.TableSet` class collects a set of related tables in a single data
structure. The most common way of creating a :class:`.TableSet` is using the
:meth:`.Table.group_by` method, which is similar to SQL's ``GROUP BY`` keyword.
The resulting set of tables will all have identical columns structure.

:class:`.TableSet` functions as a dictionary. Individual tables in the set can
be accessed by using their name as a key. If the table set was created using
:meth:`.Table.group_by` then the names of the tables will be the grouping
factors found in the original data.

:class:`.TableSet` replicates the majority of the features of :class:`.Table`.
When methods such as :meth:`.TableSet.select`, :meth:`.TableSet.where` or
:meth:`.TableSet.order_by` are used, the operation is applied to *each* table
in the set and the result is a new :class:`TableSet` instance made up of
entirely new :class:`.Table` instances.

:class:`.TableSet` instances can also contain other TableSet's. This means you
can chain calls to :meth:`.Table.group_by` and :meth:`.TableSet.group_by`
and end up with data grouped across multiple dimensions.
:meth:`.TableSet.aggregate` on nested TableSets will then group across multiple
dimensions.
"""

from io import StringIO
from itertools import zip_longest

from agate.data_types import Text
from agate.mapped_sequence import MappedSequence


class TableSet(MappedSequence):
    """
    An group of named tables with identical column definitions. Supports
    (almost) all the same operations as :class:`.Table`. When executed on a
    :class:`TableSet`, any operation that would have returned a new
    :class:`.Table` instead returns a new :class:`TableSet`. Any operation
    that would have returned a single value instead returns a dictionary of
    values.

    TableSet is implemented as a subclass of :class:`.MappedSequence`

    :param tables:
        A sequence :class:`Table` instances.
    :param keys:
        A sequence of keys corresponding to the tables. These may be any type
        except :class:`int`.
    :param key_name:
        A name that describes the grouping properties. Used as the column
        header when the groups are aggregated. Defaults to the column name that
        was grouped on.
    :param key_type:
        An instance some subclass of :class:`.DataType`. If not provided it
        will default to a :class`.Text`.
    :param _is_fork:
        Used internally to skip certain validation steps when data
        is propagated from an existing tablset.
    """
    def __init__(self, tables, keys, key_name='group', key_type=None, _is_fork=False):
        tables = tuple(tables)
        keys = tuple(keys)

        self._key_name = key_name
        self._key_type = key_type or Text()
        self._sample_table = tables[0]

        while isinstance(self._sample_table, TableSet):
            self._sample_table = self._sample_table[0]

        self._column_types = self._sample_table.column_types
        self._column_names = self._sample_table.column_names

        if not _is_fork:
            for table in tables:
                if any(not isinstance(a, type(b)) for a, b in zip_longest(table.column_types, self._column_types)):
                    raise ValueError('Not all tables have the same column types!')

                if table.column_names != self._column_names:
                    raise ValueError('Not all tables have the same column names!')

        MappedSequence.__init__(self, tables, keys)

    def __str__(self):
        """
        Print the tableset's structure via :meth:`TableSet.print_structure`.
        """
        structure = StringIO()

        self.print_structure(output=structure)

        return structure.getvalue()

    @property
    def key_name(self):
        """
        Get the name of the key this TableSet is grouped by. (If created using
        :meth:`.Table.group_by` then this is the original column name.)
        """
        return self._key_name

    @property
    def key_type(self):
        """
        Get the :class:`.DataType` this TableSet is grouped by. (If created
        using :meth:`.Table.group_by` then this is the original column type.)
        """
        return self._key_type

    @property
    def column_types(self):
        """
        Get an ordered list of this :class:`.TableSet`'s column types.

        :returns:
            A :class:`tuple` of :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        Get an ordered list of this :class:`TableSet`'s column names.

        :returns:
            A :class:`tuple` of strings.
        """
        return self._column_names

    def _fork(self, tables, keys, key_name=None, key_type=None):
        """
        Create a new :class:`.TableSet` using the metadata from this one.

        This method is used internally by functions like
        :meth:`.TableSet.having`.
        """
        if key_name is None:
            key_name = self._key_name

        if key_type is None:
            key_type = self._key_type

        return TableSet(tables, keys, key_name, key_type, _is_fork=True)

    def _proxy(self, method_name, *args, **kwargs):
        """
        Calls a method on each table in this :class:`.TableSet`.
        """
        tables = []

        for key, table in self.items():
            tables.append(getattr(table, method_name)(*args, **kwargs))

        return self._fork(
            tables,
            self.keys()
        )


from agate.tableset.aggregate import aggregate
from agate.tableset.bar_chart import bar_chart
from agate.tableset.column_chart import column_chart
from agate.tableset.from_csv import from_csv
from agate.tableset.from_json import from_json
from agate.tableset.having import having
from agate.tableset.line_chart import line_chart
from agate.tableset.merge import merge
from agate.tableset.print_structure import print_structure
from agate.tableset.proxy_methods import (bins, compute, denormalize, distinct, exclude, find, group_by, homogenize,
                                          join, limit, normalize, order_by, pivot, select, where)
from agate.tableset.scatterplot import scatterplot
from agate.tableset.to_csv import to_csv
from agate.tableset.to_json import to_json

TableSet.aggregate = aggregate
TableSet.bar_chart = bar_chart
TableSet.bins = bins
TableSet.column_chart = column_chart
TableSet.compute = compute
TableSet.denormalize = denormalize
TableSet.distinct = distinct
TableSet.exclude = exclude
TableSet.find = find
TableSet.from_csv = from_csv
TableSet.from_json = from_json
TableSet.group_by = group_by
TableSet.having = having
TableSet.homogenize = homogenize
TableSet.join = join
TableSet.limit = limit
TableSet.line_chart = line_chart
TableSet.merge = merge
TableSet.normalize = normalize
TableSet.order_by = order_by
TableSet.pivot = pivot
TableSet.print_structure = print_structure
TableSet.scatterplot = scatterplot
TableSet.select = select
TableSet.to_csv = to_csv
TableSet.to_json = to_json
TableSet.where = where
