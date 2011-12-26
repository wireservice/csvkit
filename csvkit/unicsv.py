#!/usr/bin/env python

import codecs
import csv
from cStringIO import StringIO

from csvkit.exceptions import FieldSizeLimitError

"""
The following classes are adapted from the CSV module documentation.
"""

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')

class UnicodeCSVReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, encoding='utf-8', maxfieldsize=None, **kwargs):
        f = UTF8Recoder(f, encoding)
        
        self.reader = csv.reader(f, **kwargs)

        if maxfieldsize:
            csv.field_size_limit(maxfieldsize)

    def next(self):
        try:
            row = self.reader.next()
        except csv.Error, e:
            # Terrible way to test for this exception, but there is no subclass
            if 'field larger than field limit' in str(e):
                raise FieldSizeLimitError(csv.field_size_limit())
            else:
                raise e

        return [unicode(s, 'utf-8') for s in row]

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num

class UnicodeCSVWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, encoding='utf-8', **kwargs):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s if s != None else '').encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class UnicodeCSVDictReader(csv.DictReader):
    """
    Defer almost all implementation to csv.DictReader, but wrapping our unicode reader instead
    of csv.reader.
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, *args, **kwargs):
        csv.DictReader.__init__(self, f, fieldnames, restkey, restval, *args, **kwargs)
        self.reader = UnicodeCSVReader(f, *args, **kwargs)

class UnicodeCSVDictWriter(csv.DictWriter):
    """
    Defer almost all implementation to csv.DictWriter, but wrapping our unicode reader instead
    of csv.reader
    """
    def __init__(self, f, fieldnames, writeheader=False, restval="", extrasaction="raise", *args, **kwds):
        self.fieldnames = fieldnames 
        self.restval = restval

        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError, \
                  ("extrasaction (%s) must be 'raise' or 'ignore'" %
                   extrasaction)

        self.extrasaction = extrasaction

        self.writer = UnicodeCSVWriter(f, *args, **kwds)

        if writeheader:
            self.writerow(dict(zip(self.fieldnames, self.fieldnames)))

