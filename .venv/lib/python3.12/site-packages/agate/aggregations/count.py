from agate.aggregations.base import Aggregation
from agate.data_types import Number
from agate.utils import default


class Count(Aggregation):
    """
    Count occurences of a value or values.

    This aggregation can be used in three ways:

    1. If no arguments are specified, then it will count the number of rows in the table.
    2. If only :code:`column_name` is specified, then it will count the number of non-null values in that column.
    3. If both :code:`column_name` and :code:`value` are specified, then it will count occurrences of a specific value.

    :param column_name:
        The column containing the values to be counted.
    :param value:
        Any value to be counted, including :code:`None`.
    """
    def __init__(self, column_name=None, value=default):
        self._column_name = column_name
        self._value = value

    def get_aggregate_data_type(self, table):
        return Number()

    def run(self, table):
        if self._column_name is not None:
            if self._value is not default:
                return table.columns[self._column_name].values().count(self._value)
            return len(table.columns[self._column_name].values_without_nulls())
        return len(table.rows)
