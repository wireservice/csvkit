#!/usr/bin/env python

from fixed import fixed2csv
from xls import xls2csv
from xlsx import xlsx2csv

from utils import guess_format

SUPPORTED_FORMATS = ['fixed', 'xls', 'xlsx']

def convert(f, format, schema=None):
    """
    Convert a file, f, of a specified format to CSV.
    """
    if not f:
        raise ValueError('f must not be None')

    if not format:
        raise ValueError('format must not be None')

    if format == 'fixed':
        if not schema:
            raise ValueError('schema must not be null when format is "fixed"')

        return fixed2csv(f, schema)
    elif format == 'xls':
        return xls2csv(f)
    elif format == 'xlsx':
        return xlsx2csv(f)
    else:
        raise ValueError('format "%s" is not supported' % format)

