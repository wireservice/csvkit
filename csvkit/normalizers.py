#!/usr/bin/env python

import datetime

from dateutil.parser import parse

NULL_VALUES = ('na', 'n/a', 'none', 'null', '.', '')
TRUE_VALUES = ('yes', 'y', 'true', 't')
FALSE_VALUES = ('no', 'n', 'false', 'f')

DEFAULT_DATETIME = datetime.datetime(9999, 12, 31, 0, 0, 0)
NULL_DATE = datetime.date(9999, 12, 31)
NULL_TIME = datetime.time(0, 0, 0)

def normalize_null(v):
    if v == None:
        return None

    if v.lower() in NULL_VALUES:
        return None

    raise ValueError('Not null')

def normalize_bool(v):
    if v == None:
        return None

    if v.lower() in TRUE_VALUES:
        return True

    if v.lower() in FALSE_VALUES:
        return False

    raise ValueError('Not bool')

def normalize_int(v):
    if v == None:
        return None

    x = v.replace(',', '')

    # Will raise ValueError if coercable to int
    int_x = int(x)

    if x[0] == '0' and int_x != 0:
        raise TypeError('Zero-padded number')

    return int_x

def normalize_float(v):
    if v == None:
        return None

    x = v.replace(',', '')

    # Will raise ValueError if not coercable to float
    float_x = float(x)

    if x[0] == '0' and float_x != 0:
        raise TypeError('Zero-padded number')

    return float_x

def normalize_date(v, d=None):
    if v == None:
        return None

    # Account for dateutil's habit of treating very short strings as valid
    # format strings, e.g. "a"
    if len(v) < 4:
        raise ValueError('Not a valid date')

    if not d:
        d = parse(v, default=DEFAULT_DATETIME)

    if d.date() == NULL_DATE:
        raise ValueError('Not a valid date')

    if d.time() != NULL_TIME:
        raise ValueError('Not a valid date (contains time)')

    return d.date()

def normalize_time(v, d=None):
    if v == None:
        return None

    # See note in normalize_date()
    if len(v) < 4:
        raise ValueError('Not a valid time')

    if not d:
        d = parse(v, default=DEFAULT_DATETIME)

    if d.date() != NULL_DATE:
        raise ValueError('Not a valid time')

    return d.time()

def normalize_datetime(v, d=None):
    if v == None:
        return None

    # See note in normalize_date()
    if len(v) < 4:
        raise ValueError('Not a valid datetime')

    if not d:
        d = parse(v, default=DEFAULT_DATETIME)

    # A valid date is required, but not a valid time
    if d.date() == NULL_DATE:
        raise ValueError('Not a valid datetime')

    return d

def normalize_unicode(v):
    if v == None:
        return None

    return v

