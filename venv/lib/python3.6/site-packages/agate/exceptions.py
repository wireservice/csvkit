"""
This module contains various exceptions raised by agate.
"""


class DataTypeError(TypeError):  # pragma: no cover
    """
    A calculation was attempted with an invalid :class:`.DataType`.
    """
    pass


class UnsupportedAggregationError(TypeError):  # pragma: no cover
    """
    An :class:`.Aggregation` was attempted which is not supported.

    For example, if a :class:`.Percentiles` is applied to a :class:`.TableSet`.
    """
    pass


class CastError(Exception):  # pragma: no cover
    """
    A column value can not be cast to the correct type.
    """
    pass


class FieldSizeLimitError(Exception):  # pragma: no cover
    """
    A field in a CSV file exceeds the maximum length.

    This length may be the default or one set by the user.
    """
    def __init__(self, limit, line_number):
        super().__init__(
            'CSV contains a field longer than the maximum length of %i characters on line %i. Try raising the maximum '
            'with the field_size_limit parameter, or try setting quoting=csv.QUOTE_NONE.' % (limit, line_number)
        )
