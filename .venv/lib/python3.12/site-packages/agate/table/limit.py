def limit(self, start_or_stop=None, stop=None, step=None):
    """
    Create a new table with fewer rows.

    See also: Python's builtin :func:`slice`.

    :param start_or_stop:
        If the only argument, then how many rows to include, otherwise,
        the index of the first row to include.
    :param stop:
        The index of the last row to include.
    :param step:
        The size of the jump between rows to include. (`step=2` will return
        every other row.)
    :returns:
        A new :class:`.Table`.
    """
    if stop or step:
        s = slice(start_or_stop, stop, step)
    else:
        s = slice(start_or_stop)

    rows = self._rows[s]

    if self._row_names is not None:
        row_names = self._row_names[s]
    else:
        row_names = None

    return self._fork(rows, row_names=row_names)
