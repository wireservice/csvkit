from agate import utils


def distinct(self, key=None):
    """
    Create a new table with only unique rows.

    :param key:
        Either the name of a single column to use to identify unique rows, a
        sequence of such column names, a :class:`function` that takes a
        row and returns a value to identify unique rows, or `None`, in
        which case the entire row will be checked for uniqueness.
    :returns:
        A new :class:`.Table`.
    """
    key_is_row_function = hasattr(key, '__call__')
    key_is_sequence = utils.issequence(key)

    uniques = []
    rows = []

    if self._row_names is not None:
        row_names = []
    else:
        row_names = None

    for i, row in enumerate(self._rows):
        if key_is_row_function:
            k = key(row)
        elif key_is_sequence:
            k = (row[j] for j in key)
        elif key is None:
            k = tuple(row)
        else:
            k = row[key]

        if k not in uniques:
            uniques.append(k)
            rows.append(row)

            if self._row_names is not None:
                row_names.append(self._row_names[i])

    return self._fork(rows, row_names=row_names)
