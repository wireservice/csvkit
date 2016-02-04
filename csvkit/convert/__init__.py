#!/usr/bin/env python

import agate
import agateexcel
import dbf

from csvkit.convert.fixed import fixed2csv
from csvkit.convert.geojs import geojson2csv

agateexcel.patch()

SUPPORTED_FORMATS = ['csv', 'dbf', 'fixed', 'geojson', 'json', 'ndjson', 'xls', 'xlsx']


def convert(f, format, schema=None, key=None, output=None, **kwargs):
    """
    Convert a file of a specified format to CSV.
    """
    if format == 'fixed':
        if not schema:
            raise ValueError('schema must not be null when format is "fixed"')
        output.write(fixed2csv(f, schema, output=output, **kwargs))
    elif format == 'geojson':
        output.write(geojson2csv(f, **kwargs))
    elif format in ('csv', 'dbf', 'json', 'ndjson', 'xls', 'xlsx'):
        if format == 'csv':
            table = agate.Table.from_csv(f, **kwargs)
        elif format == 'json':
            table = agate.Table.from_json(f, key=key, **kwargs)
        elif format == 'ndjson':
            table = agate.Table.from_json(f, key=key, newline=True, **kwargs)
        elif format == 'xls':
            table = agate.Table.from_xls(f, sheet=kwargs.get('sheet', None))
        elif format == 'xlsx':
            table = agate.Table.from_xlsx(f, sheet=kwargs.get('sheet', None))
        elif format == 'dbf':
            with dbf.Table(f.name) as db:
                column_names = db.field_names
                table = agate.Table(db, column_names)
        table.to_csv(output)
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

    extension = filename[last_period + 1:].lower()

    if extension in ('csv', 'dbf', 'fixed', 'xls', 'xlsx'):
        return extension
    elif extension in ['json', 'js']:
        return 'json'

    return None
