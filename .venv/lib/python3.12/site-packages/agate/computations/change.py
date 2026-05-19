from agate.aggregations.has_nulls import HasNulls
from agate.computations.base import Computation
from agate.data_types import Date, DateTime, Number, TimeDelta
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class Change(Computation):
    """
    Calculate the difference between two columns.

    This calculation can be applied to :class:`.Number` columns to calculate
    numbers. It can also be applied to :class:`.Date`, :class:`.DateTime`, and
    :class:`.TimeDelta` columns to calculate time deltas.

    :param before_column_name:
        The name of a column containing the "before" values.
    :param after_column_name:
        The name of a column containing the "after" values.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def get_computed_data_type(self, table):
        before_column = table.columns[self._before_column_name]

        if isinstance(before_column.data_type, (Date, DateTime, TimeDelta)):
            return TimeDelta()
        if isinstance(before_column.data_type, Number):
            return Number()

    def validate(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        for data_type in (Number, Date, DateTime, TimeDelta):
            if isinstance(before_column.data_type, data_type):
                if not isinstance(after_column.data_type, data_type):
                    raise DataTypeError('Specified columns must be of the same type')

                if HasNulls(self._before_column_name).run(table):
                    warn_null_calculation(self, before_column)

                if HasNulls(self._after_column_name).run(table):
                    warn_null_calculation(self, after_column)

                return

        raise DataTypeError('Change before and after columns must both contain data that is one of: '
                            'Number, Date, DateTime or TimeDelta.')

    def run(self, table):
        new_column = []

        for row in table.rows:
            before = row[self._before_column_name]
            after = row[self._after_column_name]

            if before is not None and after is not None:
                new_column.append(after - before)
            else:
                new_column.append(None)

        return new_column
