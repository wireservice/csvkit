#!/usr/bin/env python

"""
This module contains csvkit's superpowered replacement for the builtin :mod:`csv` module. For Python 2 users, the greatest improvement over the standard library full unicode support. Python 3's :mod:`csv` module supports unicode internally, so this module is provided primarily for compatability purposes.

* Python 2: :mod:`csvkit.py2`.
* Python 3: :mod:`csvkit.py3`.
"""

import six

if six.PY2:
    from csvkit import py2

    CSVKitReader = py2.CSVKitReader
    CSVKitWriter = py2.CSVKitWriter
    CSVKitDictReader = py2.CSVKitDictReader
    CSVKitDictWriter = py2.CSVKitDictWriter
    reader = py2.reader
    writer = py2.writer
    DictReader = py2.CSVKitDictReader
    DictWriter = py2.CSVKitDictWriter
else:
    from csvkit import py3

    CSVKitReader = py3.CSVKitReader
    CSVKitWriter = py3.CSVKitWriter
    CSVKitDictReader = py3.CSVKitDictReader
    CSVKitDictWriter = py3.CSVKitDictWriter
    reader = py3.reader
    writer = py3.writer
    DictReader = py3.CSVKitDictReader
    DictWriter = py3.CSVKitDictWriter

