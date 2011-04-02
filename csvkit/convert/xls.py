#!/usr/bin/env python

import csv
from cStringIO import StringIO
import datetime

import xlrd

from csvkit import typeinference
import utils

def xls2csv(f):
    """
    Convert an Excel .xls file to csv.
    """

    book = xlrd.open_workbook(file_contents=f.read())
    sheet = book.sheet_by_index(0)

    data_columns = []

    for i in range(sheet.ncols):
        # Trim headers
        column_name = sheet.col_values(i)[0]
        values = sheet.col_values(i)[1:]
        types = sheet.col_types(i)[1:]

        types_set = set(types)
        types_set.discard(xlrd.biffh.XL_CELL_EMPTY)

        if len(types_set) > 1:
            raise ValueError('Column %i ("%s") of xls file contains mixed data types. This is not supported' % (i, column_name))

        try:
            column_type = types_set.pop()
        except KeyError:
            column_type = xlrd.biffh.XL_CELL_EMPTY

        normal_values = []

        if column_type == xlrd.biffh.XL_CELL_EMPTY:
            normal_values = [None] * len(values)
        elif column_type == xlrd.biffh.XL_CELL_TEXT:
            normal_values = [v if v else None for v in values]
        elif column_type == xlrd.biffh.XL_CELL_NUMBER:
            # Test if all values are whole numbers, if so coerce floats it ints
            integral = True

            for v in values:
                if v and v % 1 != 0:
                    integral = False
                    break

            if integral:
                normal_values = [int(v) if v else None for v in values]
            else:
                # Convert blanks to None
                normal_values = [v if v else None for v in values]
        elif column_type == xlrd.biffh.XL_CELL_DATE:
            normal_values = []
            normal_types_set = set()

            for v in values:
                # Convert blanks to None
                if v == '':
                    normal_values.append(None)
                    continue

                v_tuple = xlrd.xldate_as_tuple(v, book.datemode)

                if v_tuple == (0, 0, 0, 0, 0, 0):
                    # Midnight 
                    normal_values.append(datetime.time(*v_tuple[3:]))
                    normal_types_set.add('time')
                elif v_tuple[3:] == (0, 0, 0):
                    # Date only
                    normal_values.append(datetime.date(*v_tuple[:3]))
                    normal_types_set.add('date')
                elif v_tuple[:3] == (0, 0, 0):
                    # Time only
                    normal_values.append(datetime.time(*v_tuple[3:]))
                    normal_types_set.add('time')
                else:
                    # Date and time
                    normal_values.append(datetime.datetime(*v_tuple))
                    normal_types_set.add('datetime')

            if len(normal_types_set) == 1:
                # No special handling if column contains only one type
                pass 
            elif normal_types_set == set(['datetime', 'date']):
                # If a mix of dates and datetimes, up-convert dates to datetimes
                for i, v in enumerate(normal_values):
                    if v.__class__ == datetime.date:
                        normal_values[i] = datetime.datetime.combine(v, datetime.time())
            elif normal_types_set == set(['datetime', 'time']):
                # Datetimes and times don't mix
                raise ValueError('Column %i ("%s") of xls file contains a mixes of times and datetimes.' % (i, column_name))
            elif normal_types_set == set(['date', 'time']):
                # Dates and times don't mix
                raise ValueError('Column %i ("%s") of xls file contains a mix of dates and times.' % (i, column_name))

            # Natural serialization of dates and times by csv.writer is insufficent so they get converted back to strings as part of processing.
            normal_values = [v.isoformat() if v != None else None for v in normal_values] 
        elif column_type == xlrd.biffh.XL_CELL_BOOLEAN:
            normal_values = [bool(v) if v != '' else None for v in values] 
        else:
            raise ValueError('Column %i ("%s") of xls file contains values of unsupported type "%s".' % (i, column_name, column_type))

        data_columns.append(normal_values)

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, [sheet.col_values(i)[0] for i in range(sheet.ncols)])

    return utils.rows_to_csv_string(data) 
