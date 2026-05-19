"""
This module contains a collection of utility classes and functions used in
agate.
"""

import math
import string
from collections import OrderedDict
from collections.abc import Sequence
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, getcontext
from functools import wraps

from slugify import slugify as pslugify

from agate import config
from agate.warns import warn_duplicate_column, warn_unnamed_column

#: Sentinal for use when `None` is an valid argument value
default = object()


def memoize(func):
    """
    Dead-simple memoize decorator for instance methods that take no arguments.

    This is especially useful since so many of our classes are immutable.
    """
    memo = None

    @wraps(func)
    def wrapper(self):
        if memo is not None:
            return memo

        return func(self)

    return wrapper


class NullOrder:
    """
    Dummy object used for sorting in place of None.

    Sorts as "greater than everything but other nulls."
    """
    def __lt__(self, other):
        return False

    def __eq__(self, other):
        return isinstance(other, NullOrder)

    def __gt__(self, other):
        return not isinstance(other, NullOrder)


class Quantiles(Sequence):
    """
    A class representing quantiles (percentiles, quartiles, etc.) for a given
    column of Number data.
    """
    def __init__(self, quantiles):
        self._quantiles = quantiles

    def __getitem__(self, i):
        return self._quantiles.__getitem__(i)

    def __iter__(self):
        return self._quantiles.__iter__()

    def __len__(self):
        return self._quantiles.__len__()

    def __repr__(self):
        return repr(self._quantiles)

    def __eq__(self, other):
        return self._quantiles == other._quantiles

    def locate(self, value):
        """
        Identify which quantile a given value is part of.
        """
        i = 0

        if value < self._quantiles[0]:
            raise ValueError('Value is less than minimum quantile value.')

        if value > self._quantiles[-1]:
            raise ValueError('Value is greater than maximum quantile value.')

        if value == self._quantiles[-1]:
            return Decimal(len(self._quantiles) - 1)

        while value >= self._quantiles[i + 1]:
            i += 1

        return Decimal(i)


def median(data_sorted):
    """
    Finds the median value of a given series of values.

    :param data_sorted:
        The values to find the median of. Must be sorted.
    """
    length = len(data_sorted)

    if length % 2 == 1:
        return data_sorted[((length + 1) // 2) - 1]

    half = length // 2
    a = data_sorted[half - 1]
    b = data_sorted[half]

    return (a + b) / 2


def max_precision(values):
    """
    Given a series of values (such as a :class:`.Column`) returns the most
    significant decimal places present in any value.

    :param values:
        The values to analyze.
    """
    max_whole_places = 1
    max_decimal_places = 0
    precision = getcontext().prec

    for value in values:
        if value is None or math.isnan(value) or math.isinf(value):
            continue

        sign, digits, exponent = value.normalize().as_tuple()

        exponent_places = exponent * -1
        whole_places = len(digits) - exponent_places

        if whole_places > max_whole_places:
            max_whole_places = whole_places

        if exponent_places > max_decimal_places:
            max_decimal_places = exponent_places

    # In Python 2 it was possible for the total digits to exceed the
    # available context precision. This ensures that can't happen. See #412
    if max_whole_places + max_decimal_places > precision:  # pragma: no cover
        max_decimal_places = precision - max_whole_places

    return max_decimal_places


def make_number_formatter(decimal_places, add_ellipsis=False):
    """
    Given a number of decimal places creates a formatting string that will
    display numbers with that precision.

    :param decimal_places:
        The number of decimal places
    :param add_ellipsis:
        Optionally add an ellipsis symbol at the end of a number
    """
    fraction = '0' * decimal_places
    ellipsis = config.get_option('number_truncation_chars') if add_ellipsis else ''
    return ''.join(['#,##0.', fraction, ellipsis, ';-#,##0.', fraction, ellipsis])


def round_limits(minimum, maximum):
    """
    Rounds a pair of minimum and maximum values to form reasonable "round"
    values suitable for use as axis minimum and maximum values.

    Values are rounded "out": up for maximum and down for minimum, and "off":
    to one higher than the first significant digit shared by both.

    See unit tests for examples.
    """
    min_bits = minimum.normalize().as_tuple()
    max_bits = maximum.normalize().as_tuple()

    max_digits = max(
        len(min_bits.digits) + min_bits.exponent,
        len(max_bits.digits) + max_bits.exponent
    )

    # Whole number rounding
    if max_digits > 0:
        multiplier = Decimal('10') ** (max_digits - 1)

        min_fraction = (minimum / multiplier).to_integral_value(rounding=ROUND_FLOOR)
        max_fraction = (maximum / multiplier).to_integral_value(rounding=ROUND_CEILING)

        return (
            min_fraction * multiplier,
            max_fraction * multiplier
        )

    max_exponent = max(min_bits.exponent, max_bits.exponent)

    # Fractional rounding
    q = Decimal('10') ** (max_exponent + 1)

    return (
        minimum.quantize(q, rounding=ROUND_FLOOR).normalize(),
        maximum.quantize(q, rounding=ROUND_CEILING).normalize()
    )


def letter_name(index):
    """
    Given a column index, assign a "letter" column name equivalent to
    Excel. For example, index ``4`` would return ``E``.
    Index ``30`` would return ``EE``.
    """
    letters = string.ascii_lowercase
    count = len(letters)

    return letters[index % count] * ((index // count) + 1)


def parse_object(obj, path=''):
    """
    Recursively parse JSON-like Python objects as a dictionary of paths/keys
    and values.

    Inspired by JSONPipe (https://github.com/dvxhouse/jsonpipe).
    """
    if isinstance(obj, dict):
        iterator = obj.items()
    elif isinstance(obj, (list, tuple)):
        iterator = enumerate(obj)
    else:
        return {path.strip('/'): obj}

    d = OrderedDict()

    for key, value in iterator:
        key = str(key)
        d.update(parse_object(value, path + key + '/'))

    return d


def issequence(obj):
    """
    Returns :code:`True` if the given object is an instance of
    :class:`.Sequence` that is not also a string.
    """
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def deduplicate(values, column_names=False, separator='_'):
    """
    Append a unique identifer to duplicate strings in a given sequence of
    strings. Identifers are an underscore followed by the occurance number of
    the specific string.

    ['abc', 'abc', 'cde', 'abc'] -> ['abc', 'abc_2', 'cde', 'abc_3']

    :param column_names:
        If True, values are treated as column names. Warnings will be thrown
        if column names are None or duplicates. None values will be replaced with
        letter indices.
    """
    final_values = []

    for i, value in enumerate(values):
        if column_names:
            if not value:
                new_value = letter_name(i)
                warn_unnamed_column(i, new_value)
            elif isinstance(value, str):
                new_value = value
            else:
                raise ValueError('Column names must be strings or None.')
        else:
            new_value = value

        final_value = new_value
        duplicates = 0

        while final_value in final_values:
            final_value = new_value + separator + str(duplicates + 2)
            duplicates += 1

        if column_names and duplicates > 0:
            warn_duplicate_column(new_value, final_value)

        final_values.append(final_value)

    return tuple(final_values)


def slugify(values, ensure_unique=False, **kwargs):
    """
    Given a sequence of strings, returns a standardized version of the sequence.
    If ``ensure_unique`` is True, any duplicate strings will be appended with
    a unique identifier.

    agate uses an underscore as a default separator but this can be changed with
    kwargs.

    Any kwargs will be passed to the slugify method in python-slugify. See:
    https://github.com/un33k/python-slugify
    """
    slug_args = {'separator': '_'}
    slug_args.update(kwargs)

    if ensure_unique:
        new_values = tuple(pslugify(value, **slug_args) for value in values)
        return deduplicate(new_values, separator=slug_args['separator'])

    return tuple(pslugify(value, **slug_args) for value in values)
