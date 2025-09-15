from agate.aggregations.base import Aggregation
from agate.data_types import Boolean


class Any(Aggregation):
    """
    Check if any value in a column passes a test.

    :param column_name:
        The name of the column to check.
    :param test:
        Either a single value that all values in the column are compared against
        (for equality) or a function that takes a column value and returns
        `True` or `False`.
    """
    def __init__(self, column_name, test):
        self._column_name = column_name

        if callable(test):
            self._test = test
        else:
            self._test = lambda d: d == test

    def get_aggregate_data_type(self, table):
        return Boolean()

    def validate(self, table):
        table.columns[self._column_name]

    def run(self, table):
        column = table.columns[self._column_name]
        data = column.values()

        return any(self._test(d) for d in data)
