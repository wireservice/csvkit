#!/usr/bin/env python

"""
Note: dbf is only supported/imported for Python 2.
"""

import agate
import dbf
import six

def dbf2csv(f, **kwargs):
    """
    Convert a dBASE .dbf file to csv.
    """
    with dbf.Table(f.name) as db:
        column_names = db.field_names
        table = agate.Table(db, column_names)

    output = six.StringIO()
    table.to_csv(output)
    result = output.getvalue()
    output.close()

    return result
