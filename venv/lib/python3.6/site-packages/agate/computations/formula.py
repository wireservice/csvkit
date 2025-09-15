from agate.computations.base import Computation


class Formula(Computation):
    """
    Apply an arbitrary function to each row.

    :param data_type:
        The data type this formula will return.
    :param func:
        The function to be applied to each row. Must return a valid value for
        the specified data type.
    :param cast:
        If :code:`True`, each return value will be cast to the specified
        :code:`data_type` to ensure it is valid. Only disable this if you are
        certain your formula always returns the correct type.
    """
    def __init__(self, data_type, func, cast=True):
        self._data_type = data_type
        self._func = func
        self._cast = cast

    def get_computed_data_type(self, table):
        return self._data_type

    def run(self, table):
        new_column = []

        for row in table.rows:
            v = self._func(row)

            if self._cast:
                v = self._data_type.cast(v)

            new_column.append(v)

        return new_column
