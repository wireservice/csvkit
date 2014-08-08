#!/usr/bin/env python

"""
Python3-specific classes.
"""

import csv

import six

class CSVKitReader(six.Iterator):
    """
    A unicode-aware CSV reader. Currently adds nothing to :class:`csvkit.unicsv.UnicodeCSVReader`, but might someday.
    """
    def __init__(self, f, **kwargs):
        self.reader = csv.reader(f, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader)

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num

class CSVKitWriter(object):
    """
    A unicode-aware CSV writer with some additional features.
    """
    def __init__(self, f, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers
        self._decimal_delimiter = kwargs.pop('out_decimal_delimiter', '.')
        filtered_kwargs = {
            'delimiter': kwargs.pop('out_delimiter', None),
            'doubleqoute': kwargs.pop('out_doubleqoute', None),
            'escapechar': kwargs.pop('out_escapechar', None),
            'quotechar': kwargs.pop('out_quotechar', None),
            'quoting': kwargs.pop('out_quoting', None),
            'skipinitialspace': kwargs.pop('out_skipinitialspace', None),
            'strict': kwargs.pop('out_strict', None),
            'encoding': kwargs.pop('out_encoding', 'utf-8'),
            'lineterminator': kwargs.pop('out_lineterminator', '\n')
        }
        filtered_kwargs = {k: v for k, v in filtered_kwargs.iteritems() if v is not None}
        self.writer = csv.writer(f, **filtered_kwargs)

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
        row = [i.replace('\r', '\n') if isinstance(i, six.string_types) else i for i in row]

        # Convert decimal delimiter of floats
        row = [six.text_type(i).replace('.', self._decimal_delimiter) if isinstance(i, float) else i for i in row]

        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writer.writerow(row)

class CSVKitDictReader(csv.DictReader):
    """
    A unicode-aware CSV DictReader. Currently adds nothing to :class:`csvkit.unicsv.UnicodeCSVWriter`, but might someday.
    """
    pass

class CSVKitDictWriter(csv.DictWriter):
    """
    A unicode-aware CSV DictWriter with some additional features.
    """
    def __init__(self, f, fieldnames, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers
        csv.DictWriter.__init__(self, f, fieldnames, lineterminator='\n', **kwargs)

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
        row = dict([(k, v.replace('\r', '\n')) if isinstance(v, six.string_types) else (k, v) for k, v in row.items()])

        csv.DictWriter.writerow(self, row)

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

