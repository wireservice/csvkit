from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.median import Median
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.utils import median
from agate.warns import warn_null_calculation


class MAD(Aggregation):
    """
    Calculate the `median absolute deviation <https://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of a column.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._median = Median(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('MAD can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls_sorted()
        if data:
            m = self._median.run(table)
            return median(tuple(abs(n - m) for n in data))
