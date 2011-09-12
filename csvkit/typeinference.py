#!/usr/bin/env python

import datetime

from dateutil.parser import parse

VALID_TYPE_SETS = {
        frozenset([]): None,
        frozenset([bool]): bool,
        frozenset([int]): int,
        frozenset([float]): float,
        frozenset([int, float]): float,
        frozenset([datetime.datetime]): datetime.datetime,
        frozenset([datetime.date]): datetime.date,
        frozenset([datetime.time]): datetime.time,
        frozenset([datetime.datetime, datetime.date]): datetime.datetime,
        frozenset([datetime.datetime, datetime.time]): unicode,
        frozenset([datetime.date, datetime.time]): unicode
    }

NULL_VALUES = ('na', 'n/a', 'none', 'null', '.')
TRUE_VALUES = ('yes', 'y', 'true', 't')
FALSE_VALUES = ('no', 'n', 'false', 'f')

DEFAULT_DATETIME = datetime.datetime(9999, 12, 31, 0, 0, 0)
NULL_DATE = datetime.date(9999, 12, 31)
NULL_TIME = datetime.time(0, 0, 0)

def infer_type_from_value(v):
    """
    Infers the proper type of a stringified value.
    """
    # No value?
    if v == None:
        return None
    
    # Convert "NA", "N/A", etc. to null types.
    if v.lower() in NULL_VALUES:
        v = ''

    # Is it null?
    if v == '':
        return None

    # Is it boolean?
    if v.lower() in TRUE_VALUES or v.lower() in FALSE_VALUES:
        return bool

    # Is it an integer?
    try:
        x = v.replace(',', '')
        
        int_x = int(x)

        # Zero-padding
        if x[0] == '0' and int_x != 0:
            return unicode

        return int
    except ValueError:
        pass

    # Is it a float?
    try:
        float(v.replace(',', ''))

        return float
    except ValueError:
        pass

    # Is it a datetime?
    try:
        d = parse(v, default=DEFAULT_DATETIME)

        # Is it only a time?
        if d.date() == NULL_DATE and d.time() == NULL_TIME:
            raise ValueError('Not a valid date or time.')
        if d.date() == NULL_DATE:
            return datetime.time
        # Is it only a date?
        elif d.time() == NULL_TIME:
            return datetime.date
        # It must be a date and time
        else:
            return datetime.datetime
    except ValueError:
        pass       

    # Don't know what it is, so it's a string
    return unicode 

def infer_type_from_types(types):
    """
    Infer a generic type from a list of inferred types.
    """
    types_without_nulls = set(types)
    types_without_nulls.discard(None)

    try:
        return VALID_TYPE_SETS[frozenset(types_without_nulls)]
    except KeyError:
        return unicode

def infer_types_iteratively(rows):
    """
    Iterates over the given rows and infer's the type that best matches their contents.
    Does not keep rows in memory or normalize values.

    Useful for "guessing" the types of columns based on a limited number of rows.
    When processing complete datasets it is better to use normalize_table() which will
    normalize values is optimized for processing entire columns.

    Returns a tuple of the form: (inferred_type, [all, types, seen]).
    """
    detected_types = []

    for row in rows:
        for i, v in enumerate(row):
            if i == len(detected_types):
                detected_types.append(set())

            detected_types[i].add(infer_type_from_value(v))

    normal_types = []

    for s in detected_types:
        normal_types.append((infer_type_from_types(s), s))

    return normal_types
        
def normalize_column_type(l):
    """
    Attempts to normalize a column (list) of values to booleans, integers, floats, dates, times, datetimes, or strings. NAs and missing values are converted to empty strings. Empty strings are converted to nulls.

    Returns a tuple of (type, normal_values).
    """

    # Convert "NA", "N/A", etc. to null types.
    for x in l:
        if x == None:
            continue
        elif x.lower() in NULL_VALUES:
            l[l.index(x)] = ''

    # Are they null?
    try:
        for x in l:
            if x != '':
                raise ValueError('Not null')

        return None, [None] * len(l)
    except ValueError:
        pass

    # Are they boolean?
    try:
        normal_values = []

        for x in l:
            if x == '':
                normal_values.append(None)
            elif x.lower() in TRUE_VALUES:
                normal_values.append(True)
            elif x.lower() in FALSE_VALUES:
                normal_values.append(False)
            else:
                raise ValueError('Not boolean')

        return bool, normal_values
    except ValueError:
        pass

    # Are they integers?
    try:
        normal_values = []

        for x in l:
            if x == '':
                normal_values.append(None)
                continue

            x = x.replace(',', '')
            
            int_x = int(x)

            if x[0] == '0' and int(x) != 0:
                raise TypeError('Integer is padded with 0s, so treat it as a string instead.')
            
            normal_values.append(int_x)

        return int, normal_values
    except TypeError:
        return unicode, [x if x != '' else None for x in l]
    except ValueError:
        pass

    # Are they floats?
    try:
        return float, [float(x.replace(',', '')) if x != '' else None for x in l]
    except ValueError:
        pass

    # Are they datetimes?
    try:
        normal_values = []
        normal_types_set = set()

        for x in l:
            if x == '':
                normal_values.append(None)
                continue

            d = parse(x, default=DEFAULT_DATETIME)

            # Is it only a time?
            if d.date() == NULL_DATE:
                d = d.time()
                normal_types_set.add(datetime.time)
            # Is it only a date?
            elif d.time() == NULL_TIME:
                d = d.date()
                normal_types_set.add(datetime.date)
            # It must be a date and time
            else:
                normal_types_set.add(datetime.datetime)
            
            normal_values.append(d)

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
        pass

    # Don't know what they are, so they must just be strings 
    return unicode, [x if x != '' else None for x in l]

def normalize_table(rows, column_count):
    """
    Given a sequence of sequences, normalize the lot.
    """
    data_columns = [[] for x in range(column_count)]

    for row in rows:
        for data_column, value in zip(data_columns, row):
            data_column.append(value)

    normal_types = []
    normal_columns= []

    for column in data_columns:
        t, c = normalize_column_type(column)
        normal_types.append(t)
        normal_columns.append(c)
    
    return normal_types, normal_columns

