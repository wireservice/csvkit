#!/usr/bin/env python

from csvitself import csv2csv
from fixed import fixed2csv
from js import json2csv
from xls import xls2csv
from xlsx import xlsx2csv

SUPPORTED_FORMATS = ['fixed', 'xls', 'xlsx', 'csv', 'json']

def convert(f, format, schema=None, key=None, **kwargs):
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
    elif format == 'xlsx':
        return xlsx2csv(f, **kwargs)
    elif format == 'json':
        return json2csv(f, key, **kwargs)
    elif format == 'csv':
        return csv2csv(f, **kwargs)
    else:
        raise ValueError('format "%s" is not supported' % format)

def guess_format(filename):
    """
    Try to guess a file's format based on its extension (or lack thereof).
    """
    last_period = filename.rfind('.')

    if last_period == -1:
        # No extension: assume fixed-width
        return 'fixed'

    extension = filename[last_period + 1:]

    if extension == 'xls':
        return extension
    elif extension == 'xlsx':
        return extension
    elif extension in ['json', 'js']:
        return 'json' 
    elif extension == 'csv':
        return extension
    elif extension == 'fixed':
        return extension

    return None
