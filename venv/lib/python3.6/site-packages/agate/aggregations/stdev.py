from agate.aggregations import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.variance import PopulationVariance, Variance
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class StDev(Aggregation):
    """
    Calculate the sample standard of deviation of a column.

    For the population standard of deviation see :class:`.PopulationStDev`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._variance = Variance(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('StDev can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        variance = self._variance.run(table)
        if variance is not None:
            return variance.sqrt()


class PopulationStDev(StDev):
    """
    Calculate the population standard of deviation of a column.

    For the sample standard of deviation see :class:`.StDev`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._population_variance = PopulationVariance(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationStDev can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        variance = self._population_variance.run(table)
        if variance is not None:
            return variance.sqrt()
