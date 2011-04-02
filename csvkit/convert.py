#!/usr/bin/env python

import csv
from cStringIO import StringIO
import datetime

import xlrd

from csvkit import typeinference

SUPPORTED_FORMATS = ['fixed', 'xls', 'xlsx']

def guess_format(filename):
    """
    Try to guess a file's format based on its extension (or lack thereof).
    """
    last_period = filename.rfind('.')

    if last_period == -1:
        # No extension: assume fixed-width
        return 'fixed'

    extension = filename[last_period + 1:]

    if extension == 'xlsx':
        return extension
    elif extension == 'xls':
        return extension

    return None

def fixed2csv(f, schema):
    """
    Convert a fixed-width file to csv using a CSV-formatted schema description.

    A schema CSV must start with the header row "column,start,length".
    Each subsequent row, therefore, is a column name, the starting index of the column (an integer), and the length of the column (also an integer).
    """
    NAME = 0
    START = 1
    LENGTH = 2

    schema_columns = []
    schema_reader = csv.reader(schema)

    header = schema_reader.next()

    if header != ['column', 'start', 'length']:
        raise ValueError('schema CSV must begin with a "column,start,length" header row.')

    for row in schema_reader:
        if row == 'column,start,length':
            continue

        schema_columns.append((row[NAME], int(row[START]), int(row[LENGTH])))

    # Data is processed first into columns (rather than rows) for easier type inference
    data_columns = [[] for c in schema_columns]

    for row in f:
        for i, c in enumerate(schema_columns):
            data_columns[i].append(row[c[START]:c[START] + c[LENGTH]].strip())

    # Use type-inference to normalize columns
    for column in data_columns:
        column = typeinference.infer_simple_type(column)

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, [c[NAME] for c in schema_columns])

    o = StringIO()
    writer = csv.writer(o, lineterminator='\n')
    writer.writerows(data)
    output = o.getvalue()
    o.close()

    return output

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
        types_set.discard(xlrd.biffh.XL_CELL_BLANK)

        if len(types_set) > 1:
            raise ValueError('Column %i ("%s") of xls file contains mixed data types. This is not supported' % (i, column_name))

        column_type = types_set.pop()
        normal_values = []

        if column_type == xlrd.biffh.XL_CELL_TEXT:
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
                if not v:
                    normal_values.append(None)
                    continue

                v_tuple = xlrd.xldate_as_tuple(v, book.datemode)

                if v_tuple[3:] == (0, 0, 0):
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
                pass 
            elif normal_types_set == set(['datetime', 'date']):
                # If a mix of dates and datetimes, up-convert dates to datetimes
                normal_values = [datetime.datetime.combine(v, datetime.time()) if v else None for v in normal_values]
            elif normal_types_set == set(['datetime', 'time']):
                raise ValueError('Column %i ("%s") of xls file contains a mixes of times and datetimes.' % (i, column_name))
            elif normal_types_set == set(['date', 'time']):
                raise ValueError('Column %i ("%s") of xls file contains a mix of dates and times.' % (i, column_name))
        elif column_type == xlrd.biffh.XL_CELL_BOOLEAN:
            normal_values = [bool(v) if v != '' else None for v in values] 
        else:
            raise ValueError('Column %i ("%s") of xls file contains values of unsupported type "%s".' % (i, column_name, column_type))

        data_columns.append(normal_values)

    data = zip(*data_columns)

    o = StringIO()
    writer = csv.writer(o, lineterminator='\n')
    writer.writerows(data)
    output = o.getvalue()
    o.close()

    return output

def xlsx2csv(f):
    """
    Convert an Excel .xlsx file to csv.
    """
    raise NotImplementedError()

def convert(f, format, schema=None):
    """
    Convert a file, f, of a specified format to CSV.
    """
    if not f:
        raise ValueError('f must not be None')

    if not format:
        raise ValueError('format must not be None')

    if format == 'fixed':
        if not schema:
            raise ValueError('schema must not be null when format is "fixed"')

        fixed2csv(f, schema)
    elif format == 'xls':
        xls2csv(f)
    elif format == 'xlsx':
        xlsx2csv(f)
    else:
        raise ValueError('format "%s" is not supported' % format)

