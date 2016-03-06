#!/usr/bin/env python

"""
This module contains csvkit's superpowered alternative to the standard Python
CSV reader and writer. It can be used as a drop-in replacement for the standard
module.

.. warn::

    Since version 1.0 csvkit relies on `agate <http://agate.rtfd.org>`_'s
CSV reader and writer. This module is supported for legacy purposes only and you
should migrate to using agate.
"""

import agate

reader = agate.csv.reader
writer = agate.csv.writer
DictReader = agate.csv.DictReader
DictWriter = agate.csv.DictWriter
