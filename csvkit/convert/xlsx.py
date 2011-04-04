#!/usr/bin/env python

import datetime

from openpyxl.reader.excel import load_workbook
from openpyxl.cell import Cell

import utils

def normalize_column_type(l):
    """
    Determine the correct type for a column from a list of cell types.

    NOTE: Excel/openpyxl datatypes are worthless for this purpose, so we do type inference ourselves.
    """
    # Are they null?
    try:
        for x in l:
            if x != '' and x != None:
                raise ValueError('Not null')

        return None, [None] * len(l)
    except ValueError:
        pass

    # Are they boolean?
    try:
        normal_values = []

        for x in l:
            if x in ['', None]:
                normal_values.append(None)
            elif str(x).lower() in ('1', 'yes', 'true'):
                normal_values.append(True)
            elif str(x).lower() in ('0', 'no', 'false'):
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
            if x in ['', None]:
                normal_values.append(None)
                continue

            if type(x) in [int, float] and x % 1 == 0:
                normal_values.append(int(x))
                continue

            raise ValueError('Not int')
            
        return int, normal_values 
    except ValueError:
        pass

    # Are they floats?
    try:
        normal_values = []

        for x in l:
            if x in ['', None]:
                normal_values.append(None)
                continue

            if type(x) in [int, float]:
                normal_values.append(float(x))
                continue

            raise ValueError('Not int')
            
        return float, normal_values 
    except ValueError:
        pass

    # Are they datetimes?
    try:
        normal_values = []
        normal_types_set = set()

        for v in l:
            if v in ['', None]:
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
            raise ValueError('Column contains a mix of times and datetimes (this is not supported).')
        elif normal_types_set == set([datetime.date, datetime.time]):
            # Dates and times don't mix
            raise ValueError('Column contains a mix of dates and times (this is not supported).')
            
        return normal_types_set.pop(), normal_values 
    except ValueError:
        pass

    # Don't know what they are, so they must just be strings 
    return str, [x if x not in ['', None] else None for x in l]    

def xlsx2csv(f):
    """
    Convert an Excel .xlsx file to csv.
    """
    book = load_workbook('examples/test.xlsx')
    sheet = book.worksheets[0]

    data_columns = []

    for column in sheet.columns:
        column_name = column[0].value
        values = [i.value for i in column[1:]]

        try:
            t, normal_values = normalize_column_type(values)
        except XLSXDataError, e:
            e.msg = 'Error in column %i, "%s": %s' % (i, column_name, e.msg)
            raise e

        data_columns.append(normal_values)

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, [c[0].value for c in sheet.columns])

    return utils.rows_to_csv_string(data)
