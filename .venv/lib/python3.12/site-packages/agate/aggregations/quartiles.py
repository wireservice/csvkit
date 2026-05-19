from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.percentiles import Percentiles
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.utils import Quantiles
from agate.warns import warn_null_calculation


class Quartiles(Aggregation):
    """
    Calculate the quartiles of column based on its percentiles.

    Quartiles will be equivalent to the the 25th, 50th and 75th percentiles.

    "Zeroth" (min value) and "Fourth" (max value) quartiles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.

    This aggregation can not be applied to a :class:`.TableSet`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Quartiles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        percentiles = Percentiles(self._column_name).run(table)

        return Quantiles([percentiles[i] for i in range(0, 101, 25)])
