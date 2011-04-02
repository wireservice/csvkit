#!/usr/bin/env python

import csv
from cStringIO import StringIO
import datetime
import sets

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
        values = sheet.col_values(i)[1:]
        types = sheet.col_types(i)[1:]

        types_set = sets.Set(types)
        types_set.discard(xlrd.biffh.XL_CELL_EMPTY)
        types_set.discard(xlrd.biffh.XL_CELL_BLANK)

        if len(types_set) > 1:
            raise ValueError('Column %i of xls file contains mixed data types. This is not supported' % i)

        column_type = types.pop()
        normal_values = []

        if column_type == xlrd.biffh.XL_CELL_TEXT:
            normal_values = values 
        elif column_type == xlrd.biffh.XL_CELL_NUMBER:
            # Test if all values are whole numbers, if so coerce floats it ints
            integral = True

            for v in values:
                if v % 1 != 0:
                    integral = False
                    break

            if integral:
                normal_values = [int(v) for v in values]
            else:
                normal_values = values
        elif column_type == xlrd.biffh.XL_CELL_DATE:
            datetime_values = [datetime.datetime(*xlrd.xldate_as_tuple(v, book.datemode)) for v in values]

            # Test if all values contain only dates, if so coerce datetimes to dates
            dates_only = True

            for v in datetime_values:
                if v.hour != 0 or v.minute != 0:
                    dates_only = False
                    break
            
            if dates_only:
                normal_values = [v.date() for v in datetime_values]
            else:
                # Test if all values contain only times, if so coerce datetimes to times
                times_only = True

                for v in datetime_values:
                    if v.year != 0 or v.month != 0 or v.day != 0:
                        times_only = False
                        break

                if times_only:
                    normal_values = [v.time() for v in datetime_values]
                else:
                    normal_values = datetime_values
        elif column_type == xlrd.biffh.XL_CELL_BOOLEAN:
            raise NotImplementedError()
        else:
            raise ValueError('Column %i of xls file contains values of unsupported type "%s".' % (i, column_type))

        print normal_values
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

