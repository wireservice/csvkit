#!/usr/bin/env python

from csvitself import csv2csv
from fixed import fixed2csv
from xls import xls2csv

SUPPORTED_FORMATS = ['fixed', 'xls', 'csv']

def convert(f, format, schema=None, **kwargs):
    """
    Convert a file of a specified format to CSV.
    """
    if not f:
        raise ValueError('f must not be None')

    if not format:
        raise ValueError('format must not be None')

    if format == 'fixed':
        if not schema:
            raise ValueError('schema must not be null when format is "fixed"')

        return fixed2csv(f, schema, **kwargs)
    elif format == 'xls':
        return xls2csv(f, **kwargs)
    elif format == 'csv':
        return csv2csv(f, **kwargs)
    else:
        raise ValueError('format "%s" is not supported' % format)

