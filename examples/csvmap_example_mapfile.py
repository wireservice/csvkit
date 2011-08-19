#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

def getdt(isoformat_string):
    """
        This helper method is here to demonstrate a practical use of csvmap.

        Given an ISO 8601 datetime format string (with or without offset),
        return a python datetime object.

        Accepts ISO 8601 datetime format (without offset)
        e.g., output of datetime.datetime.utcnow().isoformat()
        ex: getdt('2011-07-28T12:56:55.663700') ==> datetime.datetime(2011, 7, 28, 12, 56, 55, 663700)

        or ISO 8601 datetime format for UTC (with offset)
        e.g., output of time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime())
        or output of datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        ex: getdt('2011-08-09T14:27:56+00:00') ==> datetime.datetime(2011, 8, 9, 14, 27, 56)
    """
    formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S+00:00"]
    dt = None
    for format in formats:
        try:
            dt = datetime.datetime.strptime(isoformat_string, format)
            break
        except ValueError:
            continue
    return dt

def timestamp_created(cell=None):
    """
        Method name corresponds with slugified version of `Timéstamp Créated`,
        so it is called on every cell in the `Timéstamp Créated` column and
        the result is outputted in place of the original cell value.
    """
    if cell:
        dt = getdt(cell)
        if dt:
            return dt.strftime("%m/%d/%y")
    return cell

def companys_name(cell=None):
    """
        Method name corresponds with slugified version of `Company's Name`
        so it is called on every cell in the `Company's Name` column and
        the result is outputted in place of the original cell value.
    """
    if cell:
        return cell.upper().replace('.', '')
    return cell
