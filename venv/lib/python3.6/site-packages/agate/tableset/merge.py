from agate.rows import Row
from agate.table import Table


def merge(self, groups=None, group_name=None, group_type=None):
    """
    Convert this TableSet into a single table. This is the inverse of
    :meth:`.Table.group_by`.

    Any `row_names` set on the merged tables will be lost in this
    process.

    :param groups:
        A list of grouping factors to add to merged rows in a new column.
        If specified, it should have exactly one element per :class:`Table`
        in the :class:`TableSet`. If not specified or None, the grouping
        factor will be the name of the :class:`Row`'s original Table.
    :param group_name:
        This will be the column name of the grouping factors. If None,
        defaults to the :attr:`TableSet.key_name`.
    :param group_type:
        This will be the column type of the grouping factors. If None,
        defaults to the :attr:`TableSet.key_type`.
    :returns:
        A new :class:`Table`.
    """
    if type(groups) is not list and groups is not None:
        raise ValueError('Groups must be None or a list.')

    if type(groups) is list and len(groups) != len(self):
        raise ValueError('Groups length must be equal to TableSet length.')

    column_names = list(self._column_names)
    column_types = list(self._column_types)

    column_names.insert(0, group_name if group_name else self._key_name)
    column_types.insert(0, group_type if group_type else self._key_type)

    rows = []

    for index, (key, table) in enumerate(self.items()):
        for row in table._rows:
            if groups is None:
                rows.append(Row((key,) + tuple(row), column_names))
            else:
                rows.append(Row((groups[index],) + tuple(row), column_names))

    return Table(rows, column_names, column_types)
