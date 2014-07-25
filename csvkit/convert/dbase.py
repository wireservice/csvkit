#!/usr/bin/env python

"""
Note: dbf is only supported/imported for Python 2.
"""

import dbf
import six

from csvkit import table

def dbf2csv(f, **kwargs):
    """
    Convert a dBASE .dbf file to csv.
    """
    with dbf.Table(f.name) as db:
        headers = db.field_names

        column_ids = range(len(headers))

        data_columns = [[] for c in headers]

        for row in db:
            for i, d in enumerate(row):
                try:
                    data_columns[i].append(six.text_type(row[column_ids[i]]).strip())
                except IndexError:
                    # Non-rectangular data is truncated
                    break

        columns = []

        for i, c in enumerate(data_columns):
            columns.append(table.Column(column_ids[i], headers[i], c))

        tab = table.Table(columns=columns) 

        o = six.StringIO()
        output = tab.to_csv(o)
        output = o.getvalue()
        o.close()

        return output

