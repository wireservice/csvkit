#!/usr/bin/env python

import six

from csvkit import table

def csv2csv(f, **kwargs):
    """
    "Convert" a CSV into a new CSV by normalizing types and correcting for other anomalies.
    """
    tab = table.Table.from_csv(f, **kwargs) 

    o = six.StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output
