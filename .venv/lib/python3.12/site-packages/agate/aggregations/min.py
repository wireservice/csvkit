from agate.aggregations.base import Aggregation
from agate.data_types import Date, DateTime, Number, TimeDelta
from agate.exceptions import DataTypeError


class Min(Aggregation):
    """
    Find the minimum value in a column.

    This aggregation can be applied to columns containing :class:`.Date`,
    :class:`.DateTime`, or :class:`.Number` data.

    :param column_name:
        The name of the column to be searched.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        column = table.columns[self._column_name]

        if isinstance(column.data_type, (Date, DateTime, Number, TimeDelta)):
            return column.data_type

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, (Date, DateTime, Number, TimeDelta)):
            raise DataTypeError('Min can only be applied to columns containing DateTime, Date or Number data.')

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        if data:
            return min(data)
