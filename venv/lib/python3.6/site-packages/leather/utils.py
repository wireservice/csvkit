from collections import namedtuple
from datetime import date, datetime, timedelta
from decimal import Decimal

try:
    __IPYTHON__
    from IPython.display import SVG as IPythonSVG
except (NameError, ImportError):
    def IPythonSVG(x):
        return x


# Shorthand
ZERO = Decimal('0')
NINE_PLACES = Decimal('1e-9')

#: X data dimension index
X = 0

#: Y data dimension index
Y = 1

#: Z data dimension index
Z = 2


DIMENSION_NAMES = ['X', 'Y', 'Z']

#: Data structure for representing margins or other CSS-edge like properties
Box = namedtuple('Box', ['top', 'right', 'bottom', 'left'])

#: Data structure for a single series data point
Datum = namedtuple('Datum', ['i', 'x', 'y', 'z', 'row'])

#: Dummy object used in place of a series when rendering legends for categories
DummySeries = namedtuple('DummySeries', ['name'])


def to_year_count(d):
    """
    date > n years
    """
    return d.year


def from_year_count(n, t=date):
    """
    n years > date
    """
    return t(n, 1, 1)


def to_month_count(d):
    """
    date > n months
    """
    return (d.year * 12) + d.month


def from_month_count(n, t=date):
    """
    n months > date
    """
    return t(n // 12, (n % 12) + 1, 1)


def to_day_count(d):
    """
    date > n days
    """
    return (d - type(d).min).days


def from_day_count(n, t=date):
    """
    n days > date
    """
    return t.min + timedelta(days=n)


def to_hour_count(d):
    """
    date > n hours
    """
    return (d - datetime.min).total_seconds() / (60 * 60)


def from_hour_count(n, t=datetime):
    """
    n hours > date
    """
    return t.min + timedelta(hours=n)


def to_minute_count(d):
    """
    date > n minutes
    """
    return (d - datetime.min).total_seconds() / 60


def from_minute_count(n, t=datetime):
    """
    n minutes > date
    """
    return t.min + timedelta(minutes=n)


def to_second_count(d):
    """
    date > n seconds
    """
    return (d - datetime.min).total_seconds()


def from_second_count(n, t=datetime):
    """
    n seconds > date
    """
    return t.min + timedelta(seconds=n)


def to_microsecond_count(d):
    """
    date > n microseconds
    """
    return (d - datetime.min).total_seconds() * 1000


def from_microsecond_count(n, t=datetime):
    """
    n microseconds > date
    """
    return t.min + timedelta(microseconds=n)
