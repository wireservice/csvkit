from agate.exceptions import CastError

#: Default values which will be automatically cast to :code:`None`
DEFAULT_NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')


class DataType:  # pragma: no cover
    """
    Specifies how values should be parsed when creating a :class:`.Table`.

    :param null_values: A sequence of values which should be cast to
        :code:`None` when encountered by this data type.
    """
    def __init__(self, null_values=DEFAULT_NULL_VALUES):
        self.null_values = [v.lower() for v in null_values]

    def test(self, d):
        """
        Test, for purposes of type inference, if a value could possibly be
        coerced to this data type.

        This is really just a thin wrapper around :meth:`DataType.cast`.
        """
        try:
            self.cast(d)
        except CastError:
            return False

        return True

    def cast(self, d):
        """
        Coerce a given string value into this column's data type.
        """
        raise NotImplementedError

    def csvify(self, d):
        """
        Format a given native value for CSV serialization.
        """
        if d is None:
            return None

        return str(d)

    def jsonify(self, d):
        """
        Format a given native value for JSON serialization.
        """
        if d is None:
            return None

        return str(d)
