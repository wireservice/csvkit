from leather.data_types import DataType
from leather.utils import DIMENSION_NAMES, Datum, X, Y


class Series:
    """
    A series of data and its associated metadata.

    Series object does not modify the data it is passed.

    :param data:
        A sequence (rows) of sequences (columns), a.k.a. :func:`csv.reader`
        format. If the :code:`x` and :code:`y` are not specified then the first
        column is used as the X values and the second column is used for Y.

        Or, a sequence of (rows) of dicts (columns), a.k.a.
        :class:`csv.DictReader` format. If this format is used then :code:`x`
        and :code:`y` arguments must specify the columns to be charted.

        Or, a custom data format, in which case :code:`x` and :code:`y` must
        specify :func:`.key_function`.
    :param x:
        If using sequence row data, then this may be either an integer index
        identifying the X column, or a :func:`.key_function`.

        If using dict row data, then this may be either a key name identifying
        the X column, or a :func:`.key_function`.

        If using a custom data format, then this must be a
        :func:`.key_function`.`
    :param y:
        See :code:`x`.
    :param name:
        An optional name to be used in labeling this series. This will be
        used as the chart title if rendered in a :class:`.Lattice`.
    """
    def __init__(self, data, x=None, y=None, name=None):
        self._data = data
        self._name = name

        self._keys = [
            self._make_key(x if x is not None else X),
            self._make_key(y if y is not None else Y)
        ]

        self._types = [
            self._infer_type(X),
            self._infer_type(Y)
        ]

    def _make_key(self, key):
        """
        Process a user-specified data key and convert to a function if needed.
        """
        if callable(key):
            return key
        return lambda row, index: row[key]

    def _infer_type(self, dimension):
        """
        Infer the datatype of this column by sampling the data.
        """
        key = self._keys[dimension]

        for i, row in enumerate(self._data):
            v = key(row, i)

            if v is not None:
                break

        if v is None:
            raise ValueError('All values in %s dimension are null.' % DIMENSION_NAMES[dimension])

        return DataType.infer(v)

    @property
    def name(self):
        return self._name

    def data_type(self, dimension):
        """
        Return the data type for a dimension of this series.
        """
        return self._types[dimension]

    def data(self):
        """
        Return data for this series.
        """
        x = self._keys[X]
        y = self._keys[Y]

        for i, row in enumerate(self._data):
            yield Datum(i, x(row, i), y(row, i), None, row)

    def values(self, dimension):
        """
        Get a flattened list of values for a given dimension of the data.
        """
        key = self._keys[dimension]

        return [key(row, i) for i, row in enumerate(self._data)]

    def min(self, dimension):
        """
        Compute the minimum value of a given dimension.
        """
        return min(v for v in self.values(dimension) if v is not None)

    def max(self, dimension):
        """
        Compute the minimum value of a given dimension.
        """
        return max(v for v in self.values(dimension) if v is not None)


def key_function(row, index):
    """
    This example shows how to define a function to extract X and Y values
    from custom data.

    :param row:
        The function will be called with the row data, in whatever format it
        was provided to the :class:`.Series`.
    :param index:
        The row index in the series data will also be provided.
    :returns:
        The function must return a chartable value.
    """
    pass
