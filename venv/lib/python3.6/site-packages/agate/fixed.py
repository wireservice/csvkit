"""
This module contains a generic parser for fixed-width files. It operates
similar to Python's built-in CSV reader.
"""

from collections import OrderedDict, namedtuple

Field = namedtuple('Field', ['name', 'start', 'length'])


class Reader:
    """
    Reads a fixed-width file using a column schema in CSV format.

    This works almost exactly like Python's built-in CSV reader.

    Schemas must be in the "ffs" format, with :code:`column`, :code:`start`,
    and :code:`length` columns. There is a repository of such schemas
    maintained at `wireservice/ffs <https://github.com/wireservice/ffs>`_.
    """
    def __init__(self, f, schema_f):
        from agate import csv

        self.file = f
        self.fields = []

        reader = csv.reader(schema_f)
        header = next(reader)

        if header != ['column', 'start', 'length']:
            raise ValueError('Schema must contain exactly three columns: "column", "start", and "length".')

        for row in reader:
            self.fields.append(Field(row[0], int(row[1]), int(row[2])))

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.file)

        values = []

        for field in self.fields:
            values.append(line[field.start:field.start + field.length].strip())

        return values

    @property
    def fieldnames(self):
        """
        The names of the columns read from the schema.
        """
        return [field.name for field in self.fields]


class DictReader(Reader):
    """
    A fixed-width reader that returns :class:`collections.OrderedDict` rather
    than a list.
    """
    def __next__(self):
        line = next(self.file)
        values = OrderedDict()

        for field in self.fields:
            values[field.name] = line[field.start:field.start + field.length].strip()

        return values


def reader(*args, **kwargs):
    """
    A wrapper around :class:`.fixed.Reader`, so that it can be used in the same
    way as a normal CSV reader.
    """
    return Reader(*args, **kwargs)
