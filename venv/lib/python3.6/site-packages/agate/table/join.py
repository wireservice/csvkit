from agate import utils
from agate.rows import Row


def join(self, right_table, left_key=None, right_key=None, inner=False, full_outer=False, require_match=False,
         columns=None):
    """
    Create a new table by joining two table's on common values. This method
    implements most varieties of SQL join, in addition to some unique features.

    If :code:`left_key` and :code:`right_key` are both :code:`None` then this
    method will perform a "sequential join", which is to say it will join on row
    number. The :code:`inner` and :code:`full_outer` arguments will determine
    whether dangling left-hand and right-hand rows are included, respectively.

    If :code:`left_key` is specified, then a "left outer join" will be
    performed. This will combine columns from the :code:`right_table` anywhere
    that :code:`left_key` and :code:`right_key` are equal. Unmatched rows from
    the left table will be included with the right-hand columns set to
    :code:`None`.

    If :code:`inner` is :code:`True` then an "inner join" will be performed.
    Unmatched rows from either table will be left out.

    If :code:`full_outer` is :code:`True` then a "full outer join" will be
    performed. Unmatched rows from both tables will be included, with the
    columns in the other table set to :code:`None`.

    In all cases, if :code:`right_key` is :code:`None` then it :code:`left_key`
    will be used for both tables.

    If :code:`left_key` and :code:`right_key` are column names, the right-hand
    identifier column will not be included in the output table.

    If :code:`require_match` is :code:`True` unmatched rows will raise an
    exception. This is like an "inner join" except any row that doesn't have a
    match will raise an exception instead of being dropped. This is useful for
    enforcing expectations about datasets that should match.

    Column names from the right table which also exist in this table will
    be suffixed "2" in the new table.

    A subset of columns from the right-hand table can be included in the joined
    table using the :code:`columns` argument.

    :param right_table:
        The "right" table to join to.
    :param left_key:
        Either the name of a column from the this table to join on, the index
        of a column, a sequence of such column identifiers, a
        :class:`function` that takes a row and returns a value to join on, or
        :code:`None` in which case the tables will be joined on row number.
    :param right_key:
        Either the name of a column from :code:table` to join on, the index of
        a column, a sequence of such column identifiers, or a :class:`function`
        that takes a ow and returns a value to join on. If :code:`None` then
        :code:`left_key` will be used for both. If :code:`left_key` is
        :code:`None` then this value is ignored.
    :param inner:
        Perform a SQL-style "inner join" instead of a left outer join. Rows
        which have no match for :code:`left_key` will not be included in
        the output table.
    :param full_outer:
        Perform a SQL-style "full outer" join rather than a left or a right.
        May not be used in combination with :code:`inner`.
    :param require_match:
        If true, an exception will be raised if there is a left_key with no
        matching right_key.
    :param columns:
        A sequence of column names from :code:`right_table` to include in
        the final output table. Defaults to all columns not in
        :code:`right_key`. Ignored when :code:`full_outer` is :code:`True`.
    :returns:
        A new :class:`.Table`.
    """
    if inner and full_outer:
        raise ValueError('A join can not be both "inner" and "full_outer".')

    if right_key is None:
        right_key = left_key

    # Get join columns
    right_key_indices = []

    left_key_is_func = hasattr(left_key, '__call__')
    left_key_is_sequence = utils.issequence(left_key)

    # Left key is None
    if left_key is None:
        left_data = tuple(range(len(self._rows)))
    # Left key is a function
    elif left_key_is_func:
        left_data = [left_key(row) for row in self._rows]
    # Left key is a sequence
    elif left_key_is_sequence:
        left_columns = [self._columns[key] for key in left_key]
        left_data = zip(*[column.values() for column in left_columns])
    # Left key is a column name/index
    else:
        left_data = self._columns[left_key].values()

    right_key_is_func = hasattr(right_key, '__call__')
    right_key_is_sequence = utils.issequence(right_key)

    # Sequential join
    if left_key is None:
        right_data = tuple(range(len(right_table._rows)))
    # Right key is a function
    elif right_key_is_func:
        right_data = [right_key(row) for row in right_table._rows]
    # Right key is a sequence
    elif right_key_is_sequence:
        right_columns = [right_table._columns[key] for key in right_key]
        right_data = zip(*[column.values() for column in right_columns])
        right_key_indices = [right_table._columns._keys.index(key) for key in right_key]
    # Right key is a column name/index
    else:
        right_column = right_table._columns[right_key]
        right_data = right_column.values()
        right_key_indices = [right_table._columns.index(right_column)]

    # Build names and type lists
    column_names = list(self._column_names)
    column_types = list(self._column_types)

    for i, column in enumerate(right_table._columns):
        name = column.name

        if not full_outer:
            if columns is None and i in right_key_indices:
                continue

            if columns is not None and name not in columns:
                continue

        if name in self.column_names:
            column_names.append('%s2' % name)
        else:
            column_names.append(name)

        column_types.append(column.data_type)

    if columns is not None and not full_outer:
        right_table = right_table.select([n for n in right_table._column_names if n in columns])

    right_hash = {}

    for i, value in enumerate(right_data):
        if value not in right_hash:
            right_hash[value] = []

        right_hash[value].append(right_table._rows[i])

    # Collect new rows
    rows = []

    if self._row_names is not None and not full_outer:
        row_names = []
    else:
        row_names = None

    # Iterate over left column
    for left_index, left_value in enumerate(left_data):
        matching_rows = right_hash.get(left_value, None)

        if require_match and matching_rows is None:
            raise ValueError('Left key "%s" does not have a matching right key.' % left_value)

        # Rows with matches
        if matching_rows:
            for right_row in matching_rows:
                new_row = list(self._rows[left_index])

                for k, v in enumerate(right_row):
                    if columns is None and k in right_key_indices and not full_outer:
                        continue

                    new_row.append(v)

                rows.append(Row(new_row, column_names))

                if self._row_names is not None and not full_outer:
                    row_names.append(self._row_names[left_index])
        # Rows without matches
        elif not inner:
            new_row = list(self._rows[left_index])

            for k, v in enumerate(right_table._column_names):
                if columns is None and k in right_key_indices and not full_outer:
                    continue

                new_row.append(None)

            rows.append(Row(new_row, column_names))

            if self._row_names is not None and not full_outer:
                row_names.append(self._row_names[left_index])

    # Full outer join
    if full_outer:
        left_set = set(left_data)

        for right_index, right_value in enumerate(right_data):
            if right_value in left_set:
                continue

            new_row = ([None] * len(self._columns)) + list(right_table.rows[right_index])

            rows.append(Row(new_row, column_names))

    return self._fork(rows, column_names, column_types, row_names=row_names)
