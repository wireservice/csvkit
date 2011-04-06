#!/usr/bin/env python

import csv
import datetime

from csvkit import typeinference
import utils

def csv2csv(f, delimiter=',', quotechar='"'):
    """
    "Convert" a CSV into a new CSV by normalizing types and correcting for other anomalies.
    """
    rows = csv.reader(f, delimiter=delimiter, quotechar=quotechar) 
    headers = rows.next()

    # Data is processed first into columns (rather than rows) for easier type inference
    data_columns = [[] for c in headers]

    for row in rows:
        for i, d in enumerate(row):
            try:
                data_columns[i].append(d)
            except KeyError:
                # Non-rectangular data is truncated
                break

    # Use type-inference to normalize columns
    for column in data_columns:
        t, column = typeinference.normalize_column_type(column)

        # Stringify datetimes, dates, and times
        if t in [datetime.datetime, datetime.date, datetime.time]:
            column = [v.isoformat() if v != None else None for v in column]

    # Convert columns to rows
    data = zip(*data_columns)

    # Insert header row
    data.insert(0, headers)

    return utils.rows_to_csv_string(data)

