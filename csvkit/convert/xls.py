#!/usr/bin/env python

from cStringIO import StringIO
import datetime

import xlrd

from csvkit import table
from csvkit.exceptions import XLSDataError

def normalize_empty(values, **kwargs):
    """
    Normalize a column which contains only empty cells.
    """
    return None, [None] * len(values)

def normalize_text(values, **kwargs):
    """
    Normalize a column of text cells.
    """
    return unicode, [unicode(v) if v else None for v in values]

def normalize_numbers(values, **kwargs):
    """
    Normalize a column of numeric cells.
    """
    # Test if all values are whole numbers, if so coerce floats it ints
    integral = True

    for v in values:
        if v and v % 1 != 0:
            integral = False
            break

    if integral:
        return int, [int(v) if v != '' else None for v in values]
    else:
        # Convert blanks to None
        return float, [v if v else None for v in values]

def normalize_dates(values, datemode=0, **kwargs):
    """
    Normalize a column of date cells.
    """
    normal_values = []
    normal_types_set = set()

    for v in values:
        # Convert blanks to None
        if v == '':
            normal_values.append(None)
            continue

        v_tuple = xlrd.xldate_as_tuple(v, datemode)

        if v_tuple == (0, 0, 0, 0, 0, 0):
            # Midnight 
            normal_values.append(datetime.time(*v_tuple[3:]))
            normal_types_set.add(datetime.time)
        elif v_tuple[3:] == (0, 0, 0):
            # Date only
            normal_values.append(datetime.date(*v_tuple[:3]))
            normal_types_set.add(datetime.date)
        elif v_tuple[:3] == (0, 0, 0):
            # Time only
            normal_values.append(datetime.time(*v_tuple[3:]))
            normal_types_set.add(datetime.time)
        else:
            # Date and time
            normal_values.append(datetime.datetime(*v_tuple))
            normal_types_set.add(datetime.datetime)

    if len(normal_types_set) == 1:
        # No special handling if column contains only one type
        pass 
    elif normal_types_set == set([datetime.datetime, datetime.date]):
        # If a mix of dates and datetimes, up-convert dates to datetimes
        for i, v in enumerate(normal_values):
            if v.__class__ == datetime.date:
                normal_values[i] = datetime.datetime.combine(v, datetime.time())

        normal_types_set.remove(datetime.date)
    elif normal_types_set == set([datetime.datetime, datetime.time]):
        # Datetimes and times don't mix
        raise XLSDataError('Column contains a mix of times and datetimes (this is not supported).')
    elif normal_types_set == set([datetime.date, datetime.time]):
        # Dates and times don't mix
        raise XLSDataError('Column contains a mix of dates and times (this is not supported).')

    # Natural serialization of dates and times by csv.writer is insufficent so they get converted back to strings at this point
    return normal_types_set.pop(), normal_values

def normalize_booleans(values, **kwargs):
    """
    Normalize a column of boolean cells.
    """
    return bool, [bool(v) if v != '' else None for v in values] 

NORMALIZERS = {
    xlrd.biffh.XL_CELL_EMPTY: normalize_empty,
    xlrd.biffh.XL_CELL_TEXT: normalize_text,
    xlrd.biffh.XL_CELL_NUMBER: normalize_numbers,
    xlrd.biffh.XL_CELL_DATE: normalize_dates,
    xlrd.biffh.XL_CELL_BOOLEAN: normalize_booleans
}

def determine_column_type(types):
    """
    Determine the correct type for a column from a list of cell types.
    """
    types_set = set(types)
    types_set.discard(xlrd.biffh.XL_CELL_EMPTY)

    # Normalize mixed types to text
    if len(types_set) > 1:
        return xlrd.biffh.XL_CELL_TEXT

    try:
        return types_set.pop()
    except KeyError:
        return xlrd.biffh.XL_CELL_EMPTY

def xls2csv(f, **kwargs):
    """
    Convert an Excel .xls file to csv.
    """
    book = xlrd.open_workbook(file_contents=f.read())
    sheet = book.sheet_by_index(0)

    tab = table.Table() 

    for i in range(sheet.ncols):
        # Trim headers
        column_name = sheet.col_values(i)[0]

        values = sheet.col_values(i)[1:]
        types = sheet.col_types(i)[1:]

        column_type = determine_column_type(types)
        t, normal_values = NORMALIZERS[column_type](values, datemode=book.datemode)

        column = table.Column(i, column_name, normal_values, normal_type=t)
        tab.append(column)

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output 

