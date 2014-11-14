#!/usr/bin/env python

"""
This module contains unicode aware replacements for :func:`csv.reader` and :func:`csv.writer`. The implementations are largely copied from `examples in the csv module documentation <http://docs.python.org/library/csv.html#examples>`_.

These classes are available for Python 2 only. The Python 3 version of `csv` supports unicode internally.

.. note::

    You probably don't want to use these classes directly. Try the :mod:`csvkit` module.

"""

import codecs
import csv
import sys

import six

from csvkit.exceptions import FieldSizeLimitError

EIGHT_BIT_ENCODINGS = ['utf-8', 'u8', 'utf', 'utf8', 'latin-1', 'iso-8859-1', 'iso8859-1', '8859', 'cp819', 'latin', 'latin1', 'l1']

class UTF8Recoder(six.Iterator):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader).encode('utf-8')

class UnicodeCSVReader(object):
    """
    A CSV reader which will read rows from a file in a given encoding.
    """
    def __init__(self, f, encoding='utf-8', maxfieldsize=None, **kwargs):
        f = UTF8Recoder(f, encoding)
        
        self.reader = csv.reader(f, **kwargs)

        if maxfieldsize:
            csv.field_size_limit(maxfieldsize)

    def next(self):
        try:
            row = next(self.reader)
        except csv.Error as e:
            # Terrible way to test for this exception, but there is no subclass
            if 'field larger than field limit' in str(e):
                raise FieldSizeLimitError(csv.field_size_limit())
            else:
                raise e

        return [six.text_type(s, 'utf-8') for s in row]

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num

class UnicodeCSVWriter(object):
    """
    A CSV writer which will write rows to a file in the specified encoding.

    NB: Optimized so that eight-bit encodings skip re-encoding. See:
        https://github.com/onyxfish/csvkit/issues/175
    """
    def __init__(self, f, encoding='utf-8', **kwargs):
        self.encoding = encoding
        self._eight_bit = (self.encoding.lower().replace('_', '-') in EIGHT_BIT_ENCODINGS)

        if self._eight_bit:
            self.writer = csv.writer(f, **kwargs)
        else:
            # Redirect output to a queue for reencoding
            self.queue = six.StringIO()
            self.writer = csv.writer(self.queue, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        if self._eight_bit:
            self.writer.writerow([six.text_type(s if s != None else '').encode(self.encoding) for s in row])
        else:
            self.writer.writerow([six.text_type(s if s != None else '').encode('utf-8') for s in row])
            # Fetch UTF-8 output from the queue...
            data = self.queue.getvalue()
            data = data.decode('utf-8')
            # ...and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the file 
            self.stream.write(data)
            # empty the queue
            self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class UnicodeCSVDictReader(csv.DictReader):
    """
    Defer almost all implementation to :class:`csv.DictReader`, but wraps our unicode reader instead
    of :func:`csv.reader`.
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, *args, **kwargs):
        reader = UnicodeCSVReader(f, *args, **kwargs)

        if 'encoding' in kwargs:
            kwargs.pop('encoding')

        csv.DictReader.__init__(self, f, fieldnames, restkey, restval, *args, **kwargs)

        self.reader = reader 

class UnicodeCSVDictWriter(csv.DictWriter):
    """
    Defer almost all implementation to :class:`csv.DictWriter`, but wraps our unicode writer instead
    of :func:`csv.writer`.
    """
    def __init__(self, f, fieldnames, restval="", extrasaction="raise", *args, **kwds):
        self.fieldnames = fieldnames 
        self.restval = restval

        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'" % extrasaction)

        self.extrasaction = extrasaction

        self.writer = UnicodeCSVWriter(f, *args, **kwds)

    if sys.version_info < (2, 7):
        def writeheader(self):
            """
            Python 2.6 is missing the writeheader function.
            """
            self.writerow(dict(zip(self.fieldnames, self.fieldnames)))

