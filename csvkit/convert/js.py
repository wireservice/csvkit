#!/usr/bin/env python

import agate
import six


def json2csv(f, key=None, newline=False, **kwargs):
    """
    See `agate.Table.from_json
    <http://agate.readthedocs.org/en/1.2.0/api/table.html#agate.table.Table.from_json>`_.
    """

    table = agate.Table.from_json(f, key=key, newline=newline, **kwargs)

    output = six.StringIO()
    table.to_csv(output)
    result = output.getvalue()
    output.close()

    return result
