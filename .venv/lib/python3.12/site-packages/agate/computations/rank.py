from decimal import Decimal
from functools import cmp_to_key

from agate.computations.base import Computation
from agate.data_types import Number


class Rank(Computation):
    """
    Calculate rank order of the values in a column.

    Uses the "competition" ranking method: if there are four values and the
    middle two are tied, then the output will be `[1, 2, 2, 4]`.

    Null values will always be ranked last.

    :param column_name:
        The name of the column to rank.
    :param comparer:
        An optional comparison function. If not specified ranking will be
        ascending, with nulls ranked last.
    :param reverse:
        Reverse sort order before ranking.
    """
    def __init__(self, column_name, comparer=None, reverse=None):
        self._column_name = column_name
        self._comparer = comparer
        self._reverse = reverse

    def get_computed_data_type(self, table):
        return Number()

    def run(self, table):
        """
        :returns:
            :class:`int`
        """
        column = table.columns[self._column_name]

        if self._comparer:
            data_sorted = sorted(column.values(), key=cmp_to_key(self._comparer))
        else:
            data_sorted = column.values_sorted()

        if self._reverse:
            data_sorted.reverse()

        ranks = {}
        rank = 0

        for c in data_sorted:
            rank += 1

            if c in ranks:
                continue

            ranks[c] = Decimal(rank)

        new_column = []

        for row in table.rows:
            new_column.append(ranks[row[self._column_name]])

        return new_column
