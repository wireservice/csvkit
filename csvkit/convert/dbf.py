#!/usr/bin/env python

from cStringIO import StringIO

#import dbf
#TODO Remove one of these, add references in requirements.txt etc
from dbfpy import dbf

from csvkit import table

def dbf2csv(f, **kwargs):
    """
    Convert a dBASE .dbf file to csv.
    """
    db = dbf.Dbf(f.name)

    headers = db.fieldNames

    column_ids = range(len(headers))

    data_columns = [[] for c in headers]

    for row in db:
        for i, d in enumerate(row):
            try:
                data_columns[i].append(unicode(row[column_ids[i]]).strip())
            except IndexError:
                # Non-rectangular data is truncated
                break

    columns = []

    for i, c in enumerate(data_columns):
        columns.append(table.Column(column_ids[i], headers[i], c))
#TODO Make sure these fields are normalized

    tab = table.Table(columns=columns) 

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output
