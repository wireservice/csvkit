from collections import defaultdict

from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class Mode(Aggregation):
    """
    Calculate the mode of a column.

    :param column_name:
        The name of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Sum can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        if data:
            state = defaultdict(int)

            for n in data:
                state[n] += 1

            return max(state.keys(), key=lambda x: state[x])
