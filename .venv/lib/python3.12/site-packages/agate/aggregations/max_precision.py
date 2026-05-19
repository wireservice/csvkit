from agate.aggregations.base import Aggregation
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.utils import max_precision


class MaxPrecision(Aggregation):
    """
    Find the most decimal places present for any value in this column.

    :param column_name:
        The name of the column to be searched.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('MaxPrecision can only be applied to columns containing Number data.')

    def run(self, table):
        column = table.columns[self._column_name]

        return max_precision(column.values_without_nulls())
