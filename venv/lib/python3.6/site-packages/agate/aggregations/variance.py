from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.mean import Mean
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class Variance(Aggregation):
    """
    Calculate the sample variance of a column.

    For the population variance see :class:`.PopulationVariance`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._mean = Mean(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Variance can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        if data:
            mean = self._mean.run(table)
            return sum((n - mean) ** 2 for n in data) / (len(data) - 1)


class PopulationVariance(Variance):
    """
    Calculate the population variance of a column.

    For the sample variance see :class:`.Variance`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._mean = Mean(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationVariance can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        if data:
            mean = self._mean.run(table)
            return sum((n - mean) ** 2 for n in data) / len(data)
