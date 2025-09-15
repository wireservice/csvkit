def where(self, test):
    """
    Create a new :class:`.Table` with only those rows that pass a test.

    :param test:
        A function that takes a :class:`.Row` and returns :code:`True` if
        it should be included in the new :class:`.Table`.
    :type test:
        :class:`function`
    :returns:
        A new :class:`.Table`.
    """
    rows = []

    if self._row_names is not None:
        row_names = []
    else:
        row_names = None

    for i, row in enumerate(self._rows):
        if test(row):
            rows.append(row)

            if row_names is not None:
                row_names.append(self._row_names[i])

    return self._fork(rows, row_names=row_names)
