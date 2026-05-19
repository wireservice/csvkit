from agate.aggregations.has_nulls import HasNulls
from agate.computations.base import Computation
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class PercentChange(Computation):
    """
    Calculate the percent difference between two columns.

    :param before_column_name:
        The name of a column containing the "before" :class:`.Number` values.
    :param after_column_name:
        The name of a column containing the "after" :class:`.Number` values.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def get_computed_data_type(self, table):
        return Number()

    def validate(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        if not isinstance(before_column.data_type, Number):
            raise DataTypeError('PercentChange before column must contain Number data.')

        if not isinstance(after_column.data_type, Number):
            raise DataTypeError('PercentChange after column must contain Number data.')

        if HasNulls(self._before_column_name).run(table):
            warn_null_calculation(self, before_column)

        if HasNulls(self._after_column_name).run(table):
            warn_null_calculation(self, after_column)

    def run(self, table):
        """
        :returns:
            :class:`decimal.Decimal`
        """
        new_column = []

        for row in table.rows:
            before = row[self._before_column_name]
            after = row[self._after_column_name]

            if before is not None and after is not None:
                new_column.append((after - before) / before * 100)
            else:
                new_column.append(None)

        return new_column
