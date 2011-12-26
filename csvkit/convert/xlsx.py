#!/usr/bin/env python

from cStringIO import StringIO
import datetime
from types import NoneType

from openpyxl.reader.excel import load_workbook

from csvkit import table
from csvkit.typeinference import NULL_TIME

def normalize_empty(values, **kwargs):
    """
    Normalize a column which contains only empty cells.
    """
    return None, [None] * len(values)

def normalize_unicode(values, **kwargs):
    """
    Normalize a column of text cells.
    """
    return unicode, [unicode(v) if v else None for v in values]

def normalize_ints(values, **kwargs):
    """
    Normalize a column of integer cells.

    May also be a column of booleans represented as 0 and 1.
    """
    is_boolean = True

    for v in values:
        if v not in (0, 1, None):
            is_boolean = False
            break

    if is_boolean:
        return bool, [bool(v) if v is not None else None for v in values]

    return int, values 

def normalize_floats(values, **kwargs):
    """
    Normalize a column of float cells.
    """
    return float, [float(v) if v is not None else None for v in values]

def normalize_datetimes(values, **kwargs):
    """
    Normalize a column of datetime cells.

    May also be a column of dates with "0 time".
    """
    just_dates = True

    for v in values:
        if v and v.time() != NULL_TIME:
            just_dates = False
            break

    if just_dates:
        return datetime.date, [v.date() if v else None for v in values]
    
    # Datetimes get errant microseconds attached, have to clean them up
    #return datetime.datetime, [v.replace(microsecond=0) if v else None for v in values]

    out_values = []

    for v in values:
        if not v:
            out_values.append(None)
            continue

        if v.microsecond == 0:
            out_values.append(v)
            continue

        ms = v.microsecond

        print ms

        if ms < 1000:
            v = v.replace(microsecond=0)
        elif ms > 999000:
            v = v.replace(second=v.second + 1, microsecond=0)

        out_values.append(v)

    print out_values

    return datetime.datetime, out_values

def normalize_dates(values, **kwargs):
    """
    Normalize a column of date cells.
    """
    return datetime.date, values 

def normalize_times(values, **kwargs):
    """
    Normalize a column of date cells.
    """
    return datetime.time, values 

def normalize_booleans(values, **kwargs):
    """
    Normalize a column of boolean cells.
    """
    return bool, [bool(v) if v != '' else None for v in values] 

NORMALIZERS = {
    unicode: normalize_unicode,
    datetime.datetime: normalize_datetimes,
    datetime.date: normalize_dates,
    datetime.time: normalize_times,
    bool: normalize_booleans,
    int: normalize_ints,
    float: normalize_floats,
    NoneType: normalize_empty
}

def determine_column_type(types):
    """
    Determine the correct type for a column from a list of cell types.
    """
    types_set = set(types)
    types_set.discard(NoneType)

    if len(types_set) == 2:
        if types_set == set([int, float]):
            return float
        elif types_set == set([datetime.datetime, datetime.date]):
            return datetime.datetime

    # Normalize mixed types to text
    if len(types_set) > 1:
        return unicode

    try:
        return types_set.pop()
    except KeyError:
        return NoneType 

def xlsx2csv(f, **kwargs):
    """
    Convert an Excel .xlsx file to csv.
    """
    book = load_workbook(f)
    sheet = book.get_active_sheet()

    tab = table.Table() 

    for i, column in enumerate(sheet.columns):
        # Trim headers
        column_name = column[0].value

        # Empty column name? Truncate remaining data
        if not column_name:
            break

        values = [c.value for c in column[1:]]
        types = [type(v) for v in values]

        column_type = determine_column_type(types)
        t, normal_values = NORMALIZERS[column_type](values)

        column = table.Column(i, column_name, normal_values, normal_type=t)
        tab.append(column)

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output 

