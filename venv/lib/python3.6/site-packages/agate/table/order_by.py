from agate import utils


def order_by(self, key, reverse=False):
    """
    Create a new table that is sorted.

    :param key:
        Either the name of a single column to sort by, a sequence of such
        names, or a :class:`function` that takes a row and returns a value
        to sort by.
    :param reverse:
        If `True` then sort in reverse (typically, descending) order.
    :returns:
        A new :class:`.Table`.
    """
    if len(self._rows) == 0:
        return self._fork(self._rows)

    key_is_row_function = hasattr(key, '__call__')
    key_is_sequence = utils.issequence(key)

    def sort_key(data):
        row = data[1]

        if key_is_row_function:
            k = key(row)
        elif key_is_sequence:
            k = tuple(utils.NullOrder() if row[n] is None else row[n] for n in key)
        else:
            k = row[key]

        if k is None:
            return utils.NullOrder()

        return k

    results = sorted(enumerate(self._rows), key=sort_key, reverse=reverse)

    indices, rows = zip(*results)

    if self._row_names is not None:
        row_names = [self._row_names[i] for i in indices]
    else:
        row_names = None

    return self._fork(rows, row_names=row_names)
