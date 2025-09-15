from agate.table import Table


def _aggregate(self, aggregations=[]):
    """
    Recursive aggregation allowing for TableSet's to be nested inside
    one another.
    """
    from agate.tableset import TableSet

    output = []

    # Process nested TableSet's
    if isinstance(self._values[0], TableSet):
        for key, nested_tableset in self.items():
            column_names, column_types, nested_output, row_name_columns = _aggregate(nested_tableset, aggregations)

            for row in nested_output:
                row.insert(0, key)

                output.append(row)

        column_names.insert(0, self._key_name)
        column_types.insert(0, self._key_type)
        row_name_columns.insert(0, self._key_name)
    # Regular Tables
    else:
        column_names = [self._key_name]
        column_types = [self._key_type]
        row_name_columns = [self._key_name]

        for new_column_name, aggregation in aggregations:
            column_names.append(new_column_name)
            column_types.append(aggregation.get_aggregate_data_type(self._sample_table))

        for name, table in self.items():
            for new_column_name, aggregation in aggregations:
                aggregation.validate(table)

        for name, table in self.items():
            new_row = [name]

            for new_column_name, aggregation in aggregations:
                new_row.append(aggregation.run(table))

            output.append(new_row)

    return column_names, column_types, output, row_name_columns


def aggregate(self, aggregations):
    """
    Aggregate data from the tables in this set by performing some
    set of column operations on the groups and coalescing the results into
    a new :class:`.Table`.

    :code:`aggregations` must be a sequence of tuples, where each has two
    parts: a :code:`new_column_name` and a :class:`.Aggregation` instance.

    The resulting table will have the keys from this :class:`TableSet` (and
    any nested TableSets) set as its :code:`row_names`. See
    :meth:`.Table.__init__` for more details.

    :param aggregations:
        A list of tuples in the format :code:`(new_column_name, aggregation)`,
        where each :code:`aggregation` is an instance of :class:`.Aggregation`.
    :returns:
        A new :class:`.Table`.
    """
    column_names, column_types, output, row_name_columns = _aggregate(self, aggregations)

    if len(row_name_columns) == 1:
        row_names = row_name_columns[0]
    else:
        def row_names(r):
            return tuple(r[n] for n in row_name_columns)

    return Table(output, column_names, column_types, row_names=row_names)
