#!/usr/bin/env python

import datetime

from dateutil.parser import parse

import csvkit.normalizers

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

def infer_type_from_value(v):
    """
    Infers the proper type of a stringified value.
    """
    try:
        csvkit.normalizers.normalize_null(v)
        return None
    except ValueError:
        pass

    try:
        csvkit.normalizers.normalize_bool(v)
        return bool
    except ValueError:
        pass

    try:
        csvkit.normalizers.normalize_int(v)
        return int
    except TypeError:
        return unicode
    except ValueError:
        pass

    try:
        csvkit.normalizers.normalize_float(v)
        return float
    except TypeError:
        return unicode
    except ValueError:
        pass

    try:
        d = parse(v, default=csvkit.normalizers.DEFAULT_DATETIME)

        try:
            csvkit.normalizers.normalize_time(v, d)
            return datetime.time
        except ValueError:
            pass

        try:
            csvkit.normalizers.normalize_date(v, d)
            return datetime.date
        except ValueError:
            pass

        try:
            csvkit.normalizers.normalize_datetime(v, d)
            return datetime.datetime
        except ValueError:
            pass
    except ValueError:
        pass

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
        elif x.lower() in csvkit.normalizers.NULL_VALUES:
            l[l.index(x)] = None

    # Are they null?
    try:
        return None, [csvkit.normalizers.normalize_null(x) for x in l]
    except ValueError:
        pass

    # Are they boolean?
    try:
        return bool, [csvkit.normalizers.normalize_bool(x) for x in l]
    except ValueError:
        pass

    # Are they integers?
    try:
        return int, [csvkit.normalizers.normalize_int(x) for x in l]
    except TypeError:
        return unicode, [csvkit.normalizers.normalize_unicode(x) for x in l]
    except ValueError:
        pass

    # Are they floats?
    try:
        return float, [csvkit.normalizers.normalize_float(x) for x in l]
    except ValueError:
        pass

    try:
        lx = [parse(v, default=csvkit.normalizers.DEFAULT_DATETIME) if v != None else None for v in l]
        pairs = zip(l, lx)

        # Are they times?
        try:
            return datetime.time, [csvkit.normalizers.normalize_time(v, d) for v, d in pairs] 
        except ValueError:
            pass

        # Are they dates?
        try:
            return datetime.date, [csvkit.normalizers.normalize_date(v, d) for v, d in pairs] 
        except ValueError:
            pass

        # Are they datetimes?
        try:
            return datetime.datetime, [csvkit.normalizers.normalize_datetime(v, d) for v, d in pairs] 
        except ValueError:
            pass
    except ValueError:
        pass

    # Don't know what they are, so they must just be strings 
    return unicode, [csvkit.normalizers.normalize_unicode(x) for x in l] 

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

