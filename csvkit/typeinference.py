#!/usr/bin/env python

import datetime

from dateutil.parser import parse

DEFAULT_DATETIME = datetime.datetime(9999, 12, 31, 0, 0, 0)
NULL_DATE = datetime.date(9999, 12, 31)
NULL_TIME = datetime.time(0, 0, 0)

def normalize_column_type(l):
    """
    Attempts to normalize a column (list) of values to booleans, integers, floats, dates, times, datetimes, or strings. Empty strings are converted to nulls.

    Returns a tuple of (type, normal_values).
    """
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
            elif x.lower() in ('1', 'yes', 'y', 'true', 't'):
                normal_values.append(True)
            elif x.lower() in ('0', 'no', 'n', 'false', 'f'):
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
        return float, [float(x) if x != '' else None for x in l]
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
