from leather.series.base import Series
from leather.utils import Datum, X, Y, Z


class CategorySeries(Series):
    """
    A series of categorized data and its associated metadata.

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
    :param z:
        See :code:`y`. This variable identifies the category/sub-series of each
        row.
    :param name:
        An optional name to be used in labeling this series. This will be
        used as the chart title if rendered in a :class:`.Lattice`.
    """
    def __init__(self, data, x=None, y=None, z=None, name=None):
        self._data = data
        self._name = name

        self._keys = [
            self._make_key(x if x is not None else X),
            self._make_key(y if y is not None else Y),
            self._make_key(z if z is not None else Z)
        ]

        self._types = [
            self._infer_type(X),
            self._infer_type(Y),
            self._infer_type(Z)
        ]

    def data(self):
        """
        Return data for this series grouped for rendering.
        """
        x = self._keys[X]
        y = self._keys[Y]
        z = self._keys[Z]

        for i, row in enumerate(self._data):
            yield Datum(i, x(row, i), y(row, i), z(row, i), row)

    def categories(self):
        """
        Return all unique values in the category field.
        """
        z = self._keys[Z]
        categories = []

        for i, row in enumerate(self._data):
            cat = z(row, i)

            if cat not in categories:
                categories.append(cat)

        return categories
