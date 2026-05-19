import warnings
from decimal import Decimal, InvalidOperation

from babel.core import Locale

from agate.data_types.base import DataType
from agate.exceptions import CastError

#: A list of currency symbols sourced from `Xe <https://www.xe.com/symbols/>`_.
DEFAULT_CURRENCY_SYMBOLS = ['؋', '$', 'ƒ', '៛', '¥', '₡', '₱', '£', '€', '¢', '﷼', '₪', '₩', '₭', '₮',
                            '₦', '฿', '₤', '₫']

POSITIVE = Decimal('1')
NEGATIVE = Decimal('-1')


class Number(DataType):
    """
    Data representing numbers.

    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted numbers.
    :param group_symbol:
        A grouping symbol used in the numbers. Overrides the value provided by
        the specified :code:`locale`.
    :param decimal_symbol:
        A decimal separate symbol used in the numbers. Overrides the value
        provided by the specified :code:`locale`.
    :param currency_symbols:
        A sequence of currency symbols to strip from numbers.
    :param no_leading_zeroes:
        Whether to disallow leading zeroes.
    """
    def __init__(self, locale='en_US', group_symbol=None, decimal_symbol=None,
                 currency_symbols=DEFAULT_CURRENCY_SYMBOLS, no_leading_zeroes=None, **kwargs):
        super().__init__(**kwargs)

        self.locale = Locale.parse(locale)
        self.currency_symbols = currency_symbols
        self.no_leading_zeroes = no_leading_zeroes

        # Suppress Babel warning on Python 3.6
        # See #665
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Babel 2.14 support.
            # https://babel.pocoo.org/en/latest/changelog.html#possibly-backwards-incompatible-changes
            number_symbols = self.locale.number_symbols.get('latn', self.locale.number_symbols)
            self.group_symbol = group_symbol or number_symbols.get('group', ',')
            self.decimal_symbol = decimal_symbol or number_symbols.get('decimal', '.')

    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns:
            :class:`decimal.Decimal` or :code:`None`.
        """
        if isinstance(d, Decimal) or d is None:
            return d

        t = type(d)

        if t is int:
            return Decimal(d)
        if t is float:
            return Decimal(repr(d))
        if d is False:
            return Decimal(0)
        if d is True:
            return Decimal(1)
        if not isinstance(d, str):
            raise CastError('Can not parse value "%s" as Decimal.' % d)

        d = d.strip()

        if d.lower() in self.null_values:
            return None

        d = d.strip('%')

        if len(d) > 0 and d[0] == '-':
            d = d[1:]
            sign = NEGATIVE
        else:
            sign = POSITIVE

        for symbol in self.currency_symbols:
            d = d.strip(symbol)

        d = d.replace(self.group_symbol, '')
        d = d.replace(self.decimal_symbol, '.')

        if self.no_leading_zeroes and len(d) > 1 and d[0] == '0' and d[1] != '.':
            raise CastError('Can not parse value "%s" as Decimal without leading zeroes' % d)

        try:
            return Decimal(d) * sign
        # The Decimal class will return an InvalidOperation exception on most Python implementations,
        # but PyPy3 may return a ValueError if the string is not translatable to ASCII
        except (InvalidOperation, ValueError):
            pass

        raise CastError('Can not parse value "%s" as Decimal.' % d)

    def csvify(self, d):
        return d

    def jsonify(self, d):
        if d is None:
            return d

        return float(d)
