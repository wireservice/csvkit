#!/usr/bin/env python

import datetime

from openpyxl.reader.excel import load_workbook
from openpyxl.cell import Cell

import utils

"""
TYPE_STRING = 's'
TYPE_FORMULA = 'f'
TYPE_NUMERIC = 'n'
TYPE_BOOL = 'b'
TYPE_NULL = 's'
TYPE_INLINE = 'inlineStr'
TYPE_ERROR = 'e'
"""

class XLSXDataError(Exception):
    """
    Exception raised when there is a problem converting XLSX data.
    """
    def __init__(self, msg):
        self.msg = msg

def normalize_strings(values):
    """
    Normalize a column of text cells.
    """
    return [v if v else None for v in values]

def normalize_numerics(values):
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
        return [int(v) if v not in ('', None) else None for v in values]
    else:
        # Convert blanks to None
        return [v if v else None for v in values]

def normalize_booleans(values):
    """
    Normalize a column of boolean cells.
    """
    return [bool(v) if v != '' else None for v in values] 

def normalize_nulls(values):
    """
    Normalize a column which contains only empty cells.
    """
    return [None] * len(values)

def normalize_dates(values):
    """
    Normalize a column of date cells.
    """
    normal_values = []
    normal_types_set = set()

    for v in values:
        if v == None or v == '':
            normal_values.append(None)
            continue

        normal_values.append(v)
        normal_types_set.add(type(v))

    if len(normal_types_set) == 1:
        # No special handling if column contains only one type
        pass 
    elif normal_types_set == set([datetime.datetime, datetime.date]):
        # If a mix of dates and datetimes, up-convert dates to datetimes
        for i, v in enumerate(normal_values):
            if v.__class__ == datetime.date:
                normal_values[i] = datetime.datetime.combine(v, datetime.time())
    elif normal_types_set == set([datetime.datetime, datetime.time]):
        # Datetimes and times don't mix
        raise XLSXDataError('Column contains a mix of times and datetimes (this is not supported).')
    elif normal_types_set == set([datetime.date, datetime.time]):
        # Dates and times don't mix
        raise XLSXDataError('Column contains a mix of dates and times (this is not supported).')

    # Natural serialization of dates and times by csv.writer is insufficent so they get converted back to strings at this point
    return [v.isoformat() if v != None else None for v in normal_values] 

NORMALIZERS = {
    Cell.TYPE_STRING: normalize_strings,
    Cell.TYPE_NUMERIC: normalize_numerics,
    Cell.TYPE_BOOL: normalize_booleans,
    Cell.TYPE_NULL: normalize_nulls,
    'DATE': normalize_dates,
}

def determine_column_type(types):
    """
    Determine the correct type for a column from a list of cell types.
    """
    types_set = set(types)
    types_set.discard(Cell.TYPE_NULL)

    if len(types_set) > 1:
        raise XLSXDataError('Column contains multiple data types: %s' % str(types_set))

    try:
        return types_set.pop()
    except KeyError:
        return Cell.TYPE_NULL

def xlsx2csv(f):
    """
    Convert an Excel .xlsx file to csv.
    """
    book = load_workbook('examples/test.xlsx')
    sheet = book.worksheets[0]

    data_columns = []

    for column in sheet.columns:
        column_name = column[0]
        values = [i.value for i in column[1:]]
        types = [i.data_type if not i.is_date() else 'DATE' for i in column[1:]]

        try:
            column_type = determine_column_type(types)
             
            normal_values = NORMALIZERS[column_type](values)
        except XLSXDataError, e:
            e.msg = 'Error in column %i, "%s": %s' % (i, column_name, e.msg)
            raise e

        data_columns.append(normal_values)

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, [c[0].value for c in sheet.columns])

    return utils.rows_to_csv_string(data)
