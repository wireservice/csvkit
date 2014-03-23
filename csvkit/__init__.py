#!/usr/bin/env python

"""
This module contains csvkit's superpowered reader and writer. The greatest improvement over the standard library versions is that these versions are completely unicode aware and can support any encoding by simply passing in the its name at the time they are created.

This module defines ``reader``, ``writer``, ``DictReader`` and ``DictWriter`` so you can use it as a drop-in replacement for :mod:`csv`. Alternatively, you can instantiate :class:`CSVKitReader`, :class:`CSVKitWriter`, :class:`CSVKitDictReader` and :class:`CSVKitDictWriter` directly.
"""

from csvkit import unicsv

class CSVKitReader(unicsv.UnicodeCSVReader):
    """
    A unicode-aware CSV reader. Currently adds nothing to :class:`csvkit.unicsv.UnicodeCSVReader`, but might someday.
    """
    pass

class CSVKitWriter(unicsv.UnicodeCSVWriter):
    """
    A unicode-aware CSV writer with some additional features.
    """
    def __init__(self, f, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers
        unicsv.UnicodeCSVWriter.__init__(self, f, encoding, lineterminator='\n', **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row.insert(0, 'line_number')
        else:
            row.insert(0, self.row_count)
            
        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = [i.replace('\r', '\n') if isinstance(i, basestring) else i for i in row]

        unicsv.UnicodeCSVWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class CSVKitDictReader(unicsv.UnicodeCSVDictReader):
    """
    A unicode-aware CSV DictReader. Currently adds nothing to :class:`csvkit.unicsv.UnicodeCSVWriter`, but might someday.
    """
    pass

class CSVKitDictWriter(unicsv.UnicodeCSVDictWriter):
    """
    A unicode-aware CSV DictWriter with some additional features.
    """
    def __init__(self, f, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers
        unicsv.UnicodeCSVDictWriter.__init__(self, f, encoding, lineterminator='\n', **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row['line_number'] = 0
        else:
            row['line_number'] = self.row_count
            
        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = dict([(k, v.replace('\r', '\n')) if isinstance(v, basestring) else (k, v) for k, v in row.items()])

        unicsv.UnicodeCSVDictWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def reader(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.reader` that leverages :class:`csvkit.CSVKitReader`.
    """
    return CSVKitReader(*args, **kwargs)

def writer(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.writer` that leverages :class:`csvkit.CSVKitWriter`.
    """
    return CSVKitWriter(*args, **kwargs)

DictReader = CSVKitDictReader
DictWriter = CSVKitDictWriter
