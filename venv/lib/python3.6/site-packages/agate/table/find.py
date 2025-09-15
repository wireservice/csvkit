def find(self, test):
    """
    Find the first row that passes a test.

    :param test:
        A function that takes a :class:`.Row` and returns :code:`True` if
        it matches.
    :type test:
        :class:`function`
    :returns:
        A single :class:`.Row` if found, or `None`.
    """
    for row in self._rows:
        if test(row):
            return row

    return None
