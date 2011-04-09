#!/usr/bin/env python

from cStringIO import StringIO
import csv

from csvkit import table

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

    tab = table.Table()

    # Use type-inference to normalize columns
    for i, c in enumerate(data_columns):
        tab.append(table.Column(0, schema_columns[i][NAME], c))

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output
