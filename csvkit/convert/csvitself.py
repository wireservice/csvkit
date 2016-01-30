#!/usr/bin/env python

import agate
import six


def csv2csv(f, **kwargs):
    """
    "Convert" a CSV into a new CSV by normalizing types and correcting for other anomalies.
    """
    table = agate.Table.from_csv(f, **kwargs)

    output = six.StringIO()
    table.to_csv(output)
    result = output.getvalue()
    output.close()

    return result
