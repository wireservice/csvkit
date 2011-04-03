#!/usr/bin/env python

import datetime

from dateutil.parser import parse

DEFAULT_DATETIME = datetime.datetime(3000, 1, 1, 0, 0, 0)
DATE_ZERO = datetime.date(3000, 1, 1)
TIME_ZERO = datetime.time(0, 0, 0)

def normalize_column_type(l):
    """
    Like infer_simple_type, but will also attempt to infer dates, times, and datetimes. 
    """
    # Are they null?
    # TKTK
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
            elif x.lower() in ('1', 'yes', 'true'):
                normal_values.append(True)
            elif x.lower() in ('0', 'no', 'false'):
                normal_values.append(False)
            else:
                raise ValueError('Not boolean')

        return bool, normal_values
    except ValueError:
        pass

    # Are they integers?
    try:
        return int, [int(x) if x != '' else None for x in l]
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
            
            # Is it only a date?
            if d.time() == TIME_ZERO:
                d = d.date()
                normal_types_set.add(datetime.date)
            # Is it only a time?
            elif d.date() == DATE_ZERO:
                d = d.time()
                normal_types_set.add(datetime.time)
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
                    normal_values[i] = datetime.datetime.combine(v, TIME_ZERO)

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
    return str, [x if x != '' else None for x in l]
