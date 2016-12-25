#!/usr/bin/env python

from collections import namedtuple
from codecs import iterdecode

import agate
import six


def fixed2csv(f, schema, output=None, **kwargs):
    """
    Convert a fixed-width file to csv using a CSV-formatted schema description.

    A schema CSV must start with a header row with (at least) columns labeled
    "column","start", and "length". (Other columns will be ignored.) For each
    subsequent row, therefore, those columns will be used to identify a column
    name, the starting index of the column (an integer), and the length of the
    column (also an integer).

    Values in the 'start' column are assumed to be zero-based, unless the first
    value for 'start' is 1, in which case all values are assumed to be
    one-based.

    If output is specified, rows will be written to that object, otherwise the
    complete data will be returned.
    """
    streaming = True if output else False

    if not streaming:
        output = six.StringIO()

    try:
        encoding = kwargs['encoding']
    except KeyError:
        encoding = None

    writer = agate.csv.writer(output)

    reader = FixedWidthReader(f, schema, encoding=encoding)
    writer.writerows(reader)

    if not streaming:
        data = output.getvalue()
        output.close()

        return data

    # Return empty string when streaming
    return ''


class FixedWidthReader(six.Iterator):
    """
    Given a fixed-width file and a schema file, produce an analog to a csv
    reader that yields a row of strings for each line in the fixed-width file,
    preceded with a row of headers as provided in the schema.  (This might be
    problematic if fixed-width-files ever have header rows also, but I haven't
    seen that.)

    The schema_file should be in CSV format with a header row which has columns
    'column', 'start', and 'length'. (Other columns will be ignored.)  Values
    in the 'start' column are assumed to be "zero-based" unless the first value
    is "1" in which case all values are assumed to be "one-based."
    """

    def __init__(self, f, schema, encoding=None):
        if encoding is not None:
            f = iterdecode(f, encoding)

        self.file = f
        self.parser = FixedWidthRowParser(schema)
        self.header = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.header:
            self.header = False
            return self.parser.headers

        return self.parser.parse(next(self.file))


FixedWidthField = namedtuple('FixedWidthField', ['name', 'start', 'length'])


class FixedWidthRowParser(object):
    """
    Instantiated with a schema, able to return a sequence of trimmed strings
    representing fields given a fixed-length line. Flexible about where the
    columns are, as long as they are headed with the literal names 'column',
    'start', and 'length'.
    """

    def __init__(self, schema):
        self.fields = []  # A list of FixedWidthFields

        schema_reader = agate.csv.reader(schema)
        schema_decoder = SchemaDecoder(next(schema_reader))

        for i, row in enumerate(schema_reader):
            try:
                self.fields.append(schema_decoder(row))
            except Exception as e:
                raise ValueError("Error reading schema at line %i: %s" % (i + 2, e))

    def parse(self, line):
        values = []

        for field in self.fields:
            values.append(line[field.start:field.start + field.length].strip())

        return values

    def parse_dict(self, line):
        """
        Convenience method returns a dict. Equivalent to
        ``dict(zip(self.headers,self.parse(line)))``.
        """
        return dict(zip(self.headers, self.parse(line)))

    @property
    def headers(self):
        return [field.name for field in self.fields]


class SchemaDecoder(object):
    """
    Extracts column, start, and length columns from schema rows. Once
    instantiated, each time the instance is called with a row, a
    ``(column,start,length)`` tuple will be returned based on values in that
    row and the constructor kwargs.
    """
    REQUIRED_COLUMNS = [('column', None), ('start', int), ('length', int)]

    start = None
    length = None
    column = None
    one_based = None

    def __init__(self, header):
        """
        Constructs a schema row decoder.
        """
        for p, val_type in self.REQUIRED_COLUMNS:
            try:
                if val_type:
                    setattr(self, p, val_type(header.index(p)))
                else:
                    setattr(self, p, header.index(p))
            except ValueError:
                raise ValueError('A column named "%s" must exist in the schema file.' % (p))

    def __call__(self, row):
        """
        Return a tuple (column, start, length) based on this instance's
        parameters. If the first time this is called, the row's 'start'
        value is 1, then all 'start' values including the first will be one
        less than in the actual input data, to adjust for one-based
        specifications.  Values for 'start' and 'length' will be cast to
        integers.
        """
        if self.one_based is None:
            self.one_based = (int(row[self.start]) == 1)

        if self.one_based:
            adjusted_start = int(row[self.start]) - 1
        else:
            adjusted_start = int(row[self.start])

        return FixedWidthField(row[self.column], adjusted_start, int(row[self.length]))
