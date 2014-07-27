#!/usr/bin/env python

"""
This module contains csvkit's superpowered reader and writer. For Python 2 users, the greatest improvement over the standard library versions is that these versions are completely unicode aware and can support any encoding by simply passing in the its name at the time they are created. Python 3 resolves the unicode issues with the ``csv`` module, so this module is provided mostly for compatability purposes.

This module defines ``reader``, ``writer``, ``DictReader`` and ``DictWriter`` so you can use it as a drop-in replacement for :mod:`csv`. Alternatively, you can instantiate :class:`CSVKitReader`, :class:`CSVKitWriter`, :class:`CSVKitDictReader` and :class:`CSVKitDictWriter` directly.
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

