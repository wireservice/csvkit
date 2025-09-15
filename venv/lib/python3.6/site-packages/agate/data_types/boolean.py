from decimal import Decimal

from agate.data_types.base import DEFAULT_NULL_VALUES, DataType
from agate.exceptions import CastError

#: Default values which will be automatically cast to :code:`True`.
DEFAULT_TRUE_VALUES = ('yes', 'y', 'true', 't', '1')

#: Default values which will be automatically cast to :code:`False`.
DEFAULT_FALSE_VALUES = ('no', 'n', 'false', 'f', '0')


class Boolean(DataType):
    """
    Data representing true and false.

    Note that by default numerical `1` and `0` are considered valid boolean
    values, but other numbers are not.

    :param true_values: A sequence of values which should be cast to
        :code:`True` when encountered with this type.
    :param false_values: A sequence of values which should be cast to
        :code:`False` when encountered with this type.
    """
    def __init__(self, true_values=DEFAULT_TRUE_VALUES, false_values=DEFAULT_FALSE_VALUES,
                 null_values=DEFAULT_NULL_VALUES):
        super().__init__(null_values=null_values)

        self.true_values = true_values
        self.false_values = false_values

    def cast(self, d):
        """
        Cast a single value to :class:`bool`.

        :param d: A value to cast.
        :returns: :class:`bool` or :code:`None`.
        """
        if d is None:
            return d
        if type(d) is bool and type(d) is not int:
            return d
        if type(d) is int or isinstance(d, Decimal):
            if d == 1:
                return True
            if d == 0:
                return False
        if isinstance(d, str):
            d = d.replace(',', '').strip()

            d_lower = d.lower()

            if d_lower in self.null_values:
                return None
            if d_lower in self.true_values:
                return True
            if d_lower in self.false_values:
                return False

        raise CastError('Can not convert value %s to bool.' % d)

    def jsonify(self, d):
        return d
