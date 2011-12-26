#!/usr/bin/env python

import datetime
from types import NoneType

from dateutil.parser import parse

from exceptions import InvalidValueForTypeException, InvalidValueForTypeListException

NULL_VALUES = ('na', 'n/a', 'none', 'null', '.')
TRUE_VALUES = ('yes', 'y', 'true', 't')
FALSE_VALUES = ('no', 'n', 'false', 'f')

DEFAULT_DATETIME = datetime.datetime(9999, 12, 31, 0, 0, 0)
NULL_DATE = datetime.date(9999, 12, 31)
NULL_TIME = datetime.time(0, 0, 0)

def normalize_column_type(l, normal_type=None):
    """
    Attempts to normalize a list (column) of string values to booleans, integers,
    floats, dates, times, datetimes, or strings. NAs and missing values are converted 
    to empty strings. Empty strings are converted to nulls.

    Optional accepts a "normal_type" argument which specifies a type that the values
    must conform to (rather than inferring). Will raise InvalidValueForTypeException
    if a value is not coercable.

    Returns a tuple of (type, normal_values).
    """
    # Optimizations
    lower = unicode.lower
    replace = unicode.replace

    # Convert "NA", "N/A", etc. to null types.
    for i, x in enumerate(l):
        if x is None or lower(x) in NULL_VALUES:
            l[i] = ''

    # Are they null?
    if not normal_type or normal_type == NoneType:
        try:
            for i, x in enumerate(l):
                if x != '':
                    raise ValueError('Not null')

            return NoneType, [None] * len(l)
        except ValueError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type)

    # Are they boolean?
    if not normal_type or normal_type == bool:
        try:
            normal_values = []
            append = normal_values.append

            for i, x in enumerate(l):
                if x == '':
                    append(None)
                elif x.lower() in TRUE_VALUES:
                    append(True)
                elif x.lower() in FALSE_VALUES:
                    append(False)
                else:
                    raise ValueError('Not boolean')

            return bool, normal_values
        except ValueError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type) 

    # Are they integers?
    if not normal_type or normal_type == int:
        try:
            normal_values = []
            append = normal_values.append

            for i, x in enumerate(l):
                if x == '':
                    append(None)
                    continue
                
                int_x = int(replace(x, ',', ''))

                if x[0] == '0' and int(x) != 0:
                    raise TypeError('Integer is padded with 0s, so treat it as a string instead.')
                
                append(int_x)

            return int, normal_values
        except TypeError:
            if normal_type == int:
                raise InvalidValueForTypeException(i, x, int) 

            return unicode, [x if x != '' else None for x in l]
        except ValueError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type) 

    # Are they floats?
    if not normal_type or normal_type == float:
        try:
            normal_values = []
            append = normal_values.append

            for i, x in enumerate(l):
                if x == '':
                    append(None)
                    continue

                float_x  = float(replace(x, ',', ''))

                append(float_x)

            return float, normal_values 
        except ValueError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type) 

    # Are they datetimes?
    if not normal_type or normal_type in [datetime.time, datetime.date, datetime.datetime]:
        try:
            normal_values = []
            append = normal_values.append
            normal_types_set = set()
            add = normal_types_set.add

            for i, x in enumerate(l):
                if x == '':
                    append(None)
                    continue

                d = parse(x, default=DEFAULT_DATETIME)

                # Is it only a time?
                if d.date() == NULL_DATE:
                    if normal_type and normal_type != datetime.time:
                        raise InvalidValueForTypeException(i, x, normal_type) 

                    d = d.time()
                    add(datetime.time)
                # Is it only a date?
                elif d.time() == NULL_TIME:
                    if normal_type and normal_type not in [datetime.date, datetime.datetime]:
                        raise InvalidValueForTypeException(i, x, normal_type) 

                    d = d.date()
                    add(datetime.date)
                # It must be a date and time
                else:
                    if normal_type and normal_type != datetime.datetime:
                        raise InvalidValueForTypeException(i, x, normal_type) 

                    add(datetime.datetime)
                
                append(d)

            # No special handling if column contains only one type
            if len(normal_types_set) == 1:
                pass
            # If a mix of dates and datetimes, up-convert dates to datetimes
            elif normal_types_set == set([datetime.datetime, datetime.date]):
                for i, v in enumerate(normal_values):
                    if v.__class__ == datetime.date:
                        normal_values[i] = datetime.datetime.combine(v, NULL_TIME)

                normal_types_set.discard(datetime.date)
            # Datetimes and times don't mix -- fallback to using strings
            elif normal_types_set == set([datetime.datetime, datetime.time]):
                raise ValueError('Cant\'t coherently mix datetimes and times in a single column.') 
            # Dates and times don't mix -- fallback to using strings
            elif normal_types_set == set([datetime.date, datetime.time]):
                raise ValueError('Can\'t coherently mix dates and times in a single column.')

            return normal_types_set.pop(), normal_values 
        except ValueError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type) 
        except OverflowError:
            if normal_type:
                raise InvalidValueForTypeException(i, x, normal_type) 

    # Don't know what they are, so they must just be strings 
    return unicode, [x if x != '' else None for x in l]

def normalize_table(rows, normal_types=None, accumulate_errors=False):
    """
    Given a sequence of sequences, normalize the lot.

    Optionally accepts a normal_types parameter which is a list of
    types that the columns must normalize to.
    """
    data_columns = []
    column_count = 0
    row_count = 0

    for row in rows:
        while column_count < len(row):
            data_columns.append([None] * row_count)
            column_count += 1

        for i, value in enumerate(row):
            data_columns[i].append(value)

        row_count += 1

    new_normal_types = []
    new_normal_columns= []
    errors = {}

    for i, column in enumerate(data_columns):
        try:
            if normal_types:
                t, c = normalize_column_type(column, normal_types[i])
            else:
                t, c = normalize_column_type(column)

            new_normal_types.append(t)
            new_normal_columns.append(c)
        except InvalidValueForTypeException, e:
            if not accumulate_errors:
                raise                
        
            errors[i] = e
    
    if errors:
        raise InvalidValueForTypeListException(errors)

    return new_normal_types, new_normal_columns

