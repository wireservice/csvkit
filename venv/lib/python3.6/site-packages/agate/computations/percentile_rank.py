from agate.aggregations.percentiles import Percentiles
from agate.computations.rank import Rank
from agate.data_types import Number
from agate.exceptions import DataTypeError


class PercentileRank(Rank):
    """
    Calculate the percentile into which each value falls.

    See :class:`.Percentiles` for implementation details.

    :param column_name:
        The name of a column containing the :class:`.Number` values.
    """
    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PercentileRank column must contain Number data.')

    def run(self, table):
        """
        :returns:
            :class:`int`
        """
        percentiles = Percentiles(self._column_name).run(table)

        new_column = []

        for row in table.rows:
            new_column.append(percentiles.locate(row[self._column_name]))

        return new_column
