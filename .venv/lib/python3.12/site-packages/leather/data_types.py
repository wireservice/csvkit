from datetime import date, datetime
from decimal import Decimal


class DataType:
    """
    Base class for :class:`.Series` data types.
    """
    @classmethod
    def infer(cls, v):
        for t in [DateTime, Date, Number, Text]:
            if isinstance(v, t.types):
                return t

        raise TypeError('No data type available for %s' % type(v))


class Date(DataType):
    """
    Data representing dates.
    """
    types = (date,)


class DateTime(DataType):
    """
    Data representing dates with times.
    """
    types = (datetime,)


class Number(DataType):
    """
    Data representing numbers.
    """
    types = (int, float, Decimal)


class Text(DataType):
    """
    Data representing text/strings.
    """
    types = (str,)
