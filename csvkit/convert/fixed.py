#!/usr/bin/env python

from cStringIO import StringIO
from csvkit.unicsv import UnicodeCSVReader
from codecs import iterdecode
from csvkit import table

def fixed2csv(f, schema, **kwargs):
    """
    Convert a fixed-width file to csv using a CSV-formatted schema description.

    A schema CSV must start with the header row "column,start,length".
    Each subsequent row, therefore, is a column name, the starting index of the column (an integer), and the length of the column (also an integer).
    
    Values in the 'start' column are assumed to be zero-based, unless the first value for 'start' is 1, in which case all values are assumed to be one-based.
    """
    
    try:
        f = iterdecode(f,kwargs['encoding'])
    except KeyError: pass
    
    NAME = 0
    START = 1
    LENGTH = 2

    one_based = None

    schema_columns = []
    schema_reader = UnicodeCSVReader(schema)

    header = schema_reader.next()
    if header != ['column', 'start', 'length']:
        raise ValueError('schema CSV must begin with a "column,start,length" header row.')

    for row in schema_reader:
        if row == 'column,start,length':
            continue

        if one_based is None:
            one_based = bool(int(row[START]) == 1)
        
        if one_based:
            start = int(row[START]) - 1
        else: 
            start = int(row[START])

        schema_columns.append((row[NAME], start, int(row[LENGTH])))

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
