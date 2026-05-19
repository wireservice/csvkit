from agate.aggregations.base import Aggregation
from agate.data_types import Boolean


class HasNulls(Aggregation):
    """
    Check if the column contains null values.

    :param column_name:
        The name of the column to check.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Boolean()

    def run(self, table):
        return None in table.columns[self._column_name].values()
