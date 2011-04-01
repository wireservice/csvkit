#!/usr/bin/env python

import collections
import csv
from cStringIO import StringIO

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
    """
    COLUMN_NAME = 0
    COLUMN_START = 1
    COLUMN_LENGTH = 2

    columns = []

    schema_reader = csv.reader(schema)

    for row in schema_reader:
        columns.append((row[COLUMN_NAME], int(row[COLUMN_START]), int(row[COLUMN_LENGTH])))

    data = []
    data.append([c[COLUMN_NAME] for c in columns]) # Header

    for row in f:
        output_row = []

        for c in columns:
            datum = row[c[COLUMN_START]:c[COLUMN_START] + c[COLUMN_LENGTH]].strip()
            output_row.append(datum)

        data.append(output_row)

    o = StringIO()
    writer = csv.writer(o, lineterminator='\n')
    writer.writerows(data)
    output = o.getvalue()
    o.close()

    print output

    return output

def xls2csv(f):
    """
    Convert an Excel .xls file to csv.
    """
    raise NotImplementedError()

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

