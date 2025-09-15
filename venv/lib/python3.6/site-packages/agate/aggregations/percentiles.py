import math

from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.utils import Quantiles
from agate.warns import warn_null_calculation


class Percentiles(Aggregation):
    """
    Divide a column into 100 equal-size groups using the "CDF" method.

    See `this explanation <http://www.amstat.org/publications/jse/v14n3/langford.html>`_
    of the various methods for computing percentiles.

    "Zeroth" (min value) and "Hundredth" (max value) percentiles are included
    for reference and intuitive indexing.

    A reference implementation was provided by
    `pycalcstats <https://code.google.com/p/pycalcstats/>`_.

    This aggregation can not be applied to a :class:`.TableSet`.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Percentiles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        column = table.columns[self._column_name]

        data = column.values_without_nulls_sorted()

        if not data:
            return Quantiles([None for percentile in range(101)])

        # Zeroth percentile is first datum
        quantiles = [data[0]]

        for percentile in range(1, 100):
            k = len(data) * (float(percentile) / 100)

            low = max(1, int(math.ceil(k)))
            high = min(len(data), int(math.floor(k + 1)))

            # No remainder
            if low == high:
                value = data[low - 1]
            # Remainder
            else:
                value = (data[low - 1] + data[high - 1]) / 2

            quantiles.append(value)

        # Hundredth percentile is final datum
        quantiles.append(data[-1])

        return Quantiles(quantiles)
