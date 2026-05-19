from agate import utils
from agate.rows import Row


def select(self, key):
    """
    Create a new table with only the specified columns.

    :param key:
        Either the name of a single column to include or a sequence of such
        names.
    :returns:
        A new :class:`.Table`.
    """
    if not utils.issequence(key):
        key = [key]

    indexes = tuple(self._column_names.index(k) for k in key)
    column_types = tuple(self._column_types[i] for i in indexes)
    new_rows = []

    for row in self._rows:
        new_rows.append(Row((row[i] for i in indexes), key))

    return self._fork(new_rows, key, column_types)
