from agate.aggregations.base import Aggregation


class Summary(Aggregation):
    """
    Apply an arbitrary function to a column.

    :param column_name:
        The name of a column to be summarized.
    :param data_type:
        The return type of this aggregation.
    :param func:
        A function which will be passed the column for processing.
    :param cast:
        If :code:`True`, each return value will be cast to the specified
        :code:`data_type` to ensure it is valid. Only disable this if you are
        certain your summary always returns the correct type.
    """
    def __init__(self, column_name, data_type, func, cast=True):
        self._column_name = column_name
        self._data_type = data_type
        self._func = func
        self._cast = cast

    def get_aggregate_data_type(self, table):
        return self._data_type

    def run(self, table):
        v = self._func(table.columns[self._column_name])

        if self._cast:
            v = self._data_type.cast(v)

        return v
