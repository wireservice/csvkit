#!/usr/bin/env python

import agate
import agateexcel
import six

agateexcel.patch()


def xls2csv(f, **kwargs):
    """
    Convert an Excel .xls file to csv.
    """
    table = agate.Table.from_xls(f, sheet=kwargs.get('sheet', None))

    o = six.StringIO()
    output = table.to_csv(o)
    output = o.getvalue()
    o.close()

    return output
