import datetime

from agate.aggregations.base import Aggregation
from agate.data_types import Number, TimeDelta
from agate.exceptions import DataTypeError


class Sum(Aggregation):
    """
    Calculate the sum of a column.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        column = table.columns[self._column_name]

        if isinstance(column.data_type, (Number, TimeDelta)):
            return column.data_type

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, (Number, TimeDelta)):
            raise DataTypeError('Sum can only be applied to columns containing Number or TimeDelta data.')

    def run(self, table):
        column = table.columns[self._column_name]

        start = 0
        if isinstance(column.data_type, TimeDelta):
            start = datetime.timedelta()

        return sum(column.values_without_nulls(), start)
