#!/usr/bin/env python

"""
Note: dbf is only supported/imported for Python 2.
"""

from datetime import date, datetime
from decimal import Decimal

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

    o = six.StringIO()
    output = table.to_csv(o)
    output = o.getvalue()
    o.close()

    return output
