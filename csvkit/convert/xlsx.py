#!/usr/bin/env python

from openpyxl.reader.excel import load_workbook
from openpyxl.cell import Cell

import utils

"""
    Cell.TYPE_STRING = 's'
    TYPE_FORMULA = 'f'
    TYPE_NUMERIC = 'n'
    TYPE_BOOL = 'b'
    TYPE_NULL = 's'
    TYPE_INLINE = 'inlineStr'
    TYPE_ERROR = 'e'
"""

def normalize_string(values):
    raise NotImpelementedError()

def normalize_numeric(values):
    raise NotImplementedError()

def normalize_booleans(values):
    raise NotImplementedError()

def normalize_nulls(values):
    raise NotImplementedError()

def normalize_dates(values):
    raise NotImplementedError()

NORMALIZERS = {
    Cell.TYPE_STRING: normalize_string,
    Cell.TYPE_NUMERIC: normalize_numeric,
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
    book = load_workbook('examples/test.xls')
    sheet = book.worksheets[0]

    data_columns = []

    for column in sheet.columns:
        column_name = column[0]
        values = [i.value for i in column[1:]]
        types = [i.datatype if not i.is_date() else 'DATE' for i in column[1:]]

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
    # TKTK

    raise utils.rows_to_csv_string(data)
