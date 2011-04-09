#!/usr/bin/env python

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
    elif extension == 'csv':
        return extension
    elif extension == 'fixed':
        return extension

    return None
