#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
timeparse.py
(c) Will Roberts <wildwilhelm@gmail.com>  1 February, 2014

Implements a single function, `timeparse`, which can parse various
kinds of time expressions.
'''

# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

SIGN        = r'(?P<sign>[+|-])?'
#YEARS      = r'(?P<years>\d+)\s*(?:ys?|yrs?.?|years?)'
#MONTHS     = r'(?P<months>\d+)\s*(?:mos?.?|mths?.?|months?)'
WEEKS       = r'(?P<weeks>[\d.]+)\s*(?:w|wks?|weeks?)'
DAYS        = r'(?P<days>[\d.]+)\s*(?:d|dys?|days?)'
HOURS       = r'(?P<hours>[\d.]+)\s*(?:h|hrs?|hours?)'
MINS        = r'(?P<mins>[\d.]+)\s*(?:m|(mins?)|(minutes?))'
SECS        = r'(?P<secs>[\d.]+)\s*(?:s|secs?|seconds?)'
SEPARATORS  = r'[,/]'
SECCLOCK    = r':(?P<secs>\d{2}(?:\.\d+)?)'
MINCLOCK    = r'(?P<mins>\d{1,2}):(?P<secs>\d{2}(?:\.\d+)?)'
HOURCLOCK   = r'(?P<hours>\d+):(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)'
DAYCLOCK    = (r'(?P<days>\d+):(?P<hours>\d{2}):'
               r'(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)')

OPT         = lambda x: r'(?:{x})?'.format(x=x, SEPARATORS=SEPARATORS)
OPTSEP      = lambda x: r'(?:{x}\s*(?:{SEPARATORS}\s*)?)?'.format(
    x=x, SEPARATORS=SEPARATORS)

TIMEFORMATS = [
    r'{WEEKS}\s*{DAYS}\s*{HOURS}\s*{MINS}\s*{SECS}'.format(
        #YEARS=OPTSEP(YEARS),
        #MONTHS=OPTSEP(MONTHS),
        WEEKS=OPTSEP(WEEKS),
        DAYS=OPTSEP(DAYS),
        HOURS=OPTSEP(HOURS),
        MINS=OPTSEP(MINS),
        SECS=OPT(SECS)),
    r'{MINCLOCK}'.format(
        MINCLOCK=MINCLOCK),
    r'{WEEKS}\s*{DAYS}\s*{HOURCLOCK}'.format(
        WEEKS=OPTSEP(WEEKS),
        DAYS=OPTSEP(DAYS),
        HOURCLOCK=HOURCLOCK),
    r'{DAYCLOCK}'.format(
        DAYCLOCK=DAYCLOCK),
    r'{SECCLOCK}'.format(
        SECCLOCK=SECCLOCK),
    #r'{YEARS}'.format(
        #YEARS=YEARS),
    #r'{MONTHS}'.format(
        #MONTHS=MONTHS),
    ]

COMPILED_SIGN = re.compile(r'\s*' + SIGN + r'\s*(?P<unsigned>.*)$')
COMPILED_TIMEFORMATS = [re.compile(r'\s*' + timefmt + r'\s*$', re.I)
                        for timefmt in TIMEFORMATS]

MULTIPLIERS = dict([
        #('years',  60 * 60 * 24 * 365),
        #('months', 60 * 60 * 24 * 30),
        ('weeks',   60 * 60 * 24 * 7),
        ('days',    60 * 60 * 24),
        ('hours',   60 * 60),
        ('mins',    60),
        ('secs',    1)
        ])

def _interpret_as_minutes(sval, mdict):
    """
    Times like "1:22" are ambiguous; do they represent minutes and seconds
    or hours and minutes?  By default, timeparse assumes the latter.  Call
    this function after parsing out a dictionary to change that assumption.
    
    >>> import pprint
    >>> pprint.pprint(_interpret_as_minutes('1:24', {'secs': '24', 'mins': '1'}))
    {'hours': '1', 'mins': '24'}
    """
    if (    sval.count(':') == 1 
        and '.' not in sval
        and (('hours' not in mdict) or (mdict['hours'] is None))
        and (('days' not in mdict) or (mdict['days'] is None))
        and (('weeks' not in mdict) or (mdict['weeks'] is None))
        #and (('months' not in mdict) or (mdict['months'] is None))
        #and (('years' not in mdict) or (mdict['years'] is None))
        ):   
        mdict['hours'] = mdict['mins']
        mdict['mins'] = mdict['secs']
        mdict.pop('secs')
        pass
    return mdict

def timeparse(sval, granularity='seconds'):
    '''
    Parse a time expression, returning it as a number of seconds.  If
    possible, the return value will be an `int`; if this is not
    possible, the return will be a `float`.  Returns `None` if a time
    expression cannot be parsed from the given string.

    Arguments:
    - `sval`: the string value to parse

    >>> timeparse('1:24')
    84
    >>> timeparse(':22')
    22
    >>> timeparse('1 minute, 24 secs')
    84
    >>> timeparse('1m24s')
    84
    >>> timeparse('1.2 minutes')
    72
    >>> timeparse('1.2 seconds')
    1.2

    Time expressions can be signed.

    >>> timeparse('- 1 minute')
    -60
    >>> timeparse('+ 1 minute')
    60
    
    If granularity is specified as ``minutes``, then ambiguous digits following
    a colon will be interpreted as minutes; otherwise they are considered seconds.
    
    >>> timeparse('1:30')
    90
    >>> timeparse('1:30', granularity='minutes')
    5400
    '''
    match = COMPILED_SIGN.match(sval)
    sign = -1 if match.groupdict()['sign'] == '-' else 1
    sval = match.groupdict()['unsigned']
    for timefmt in COMPILED_TIMEFORMATS:
        match = timefmt.match(sval)
        if match and match.group(0).strip():
            mdict = match.groupdict()
            if granularity == 'minutes':
                mdict = _interpret_as_minutes(sval, mdict)
            # if all of the fields are integer numbers
            if all(v.isdigit() for v in list(mdict.values()) if v):
                return sign * sum([MULTIPLIERS[k] * int(v, 10) for (k, v) in
                            list(mdict.items()) if v is not None])
            # if SECS is an integer number
            elif ('secs' not in mdict or
                  mdict['secs'] is None or
                  mdict['secs'].isdigit()):
                # we will return an integer
                return (
                    sign * int(sum([MULTIPLIERS[k] * float(v) for (k, v) in
                             list(mdict.items()) if k != 'secs' and v is not None])) +
                    (int(mdict['secs'], 10) if mdict['secs'] else 0))
            else:
                # SECS is a float, we will return a float
                return sign * sum([MULTIPLIERS[k] * float(v) for (k, v) in
                            list(mdict.items()) if v is not None])
