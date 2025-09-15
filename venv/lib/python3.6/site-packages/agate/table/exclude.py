from agate import utils


def exclude(self, key):
    """
    Create a new table without the specified columns.

    :param key:
        Either the name of a single column to exclude or a sequence of such
        names.
    :returns:
        A new :class:`.Table`.
    """
    if not utils.issequence(key):
        key = [key]

    selected_column_names = tuple(n for n in self._column_names if n not in key)

    return self.select(selected_column_names)
