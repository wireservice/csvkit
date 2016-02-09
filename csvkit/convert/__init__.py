#!/usr/bin/env python


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
