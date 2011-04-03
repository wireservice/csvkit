#!/usr/bin/env python

import csv
import datetime

from csvkit import typeinference
import utils

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
        t, column = typeinference.normalize_column_type(column)

        # Stringify datetimes, dates, and times
        if t in [datetime.datetime, datetime.date, datetime.time]:
            column = [v.isoformat() if v != None else None for v in column]

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, [c[NAME] for c in schema_columns])

    return utils.rows_to_csv_string(data)
