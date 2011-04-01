#!/usr/bin/env python

import csv
from cStringIO import StringIO

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

    data_columns = [sheet.col_values(i) for i in range(sheet.ncols)]

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

