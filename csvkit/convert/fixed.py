#!/usr/bin/env python

from cStringIO import StringIO
from csvkit.unicsv import UnicodeCSVReader, UnicodeCSVWriter
from codecs import iterdecode
from csvkit import table

def fixed2csv(f, schema, **kwargs):
    """
    Convert a fixed-width file to csv using a CSV-formatted schema description.

    A schema CSV must start with a header row with (at least) columns labeled "column","start", and "length". (Other columns will be ignored.) For each subsequent row, therefore, those columns will be used to identify a column name, the starting index of the column (an integer), and the length of the column (also an integer).
    
    Values in the 'start' column are assumed to be zero-based, unless the first value for 'start' is 1, in which case all values are assumed to be one-based.
    """
    
    try:
        f = iterdecode(f,kwargs['encoding'])
    except KeyError: pass
    
    NAME = 0
    START = 1
    LENGTH = 2

    parser = SchematicLineParser(schema)
    # Data is processed first into columns (rather than rows) for easier type inference
    data_columns = [[] for h in parser.headers]

    for row in f:
        for i, c in enumerate(parser.parse(row)):
            data_columns[i].append(c)

    tab = table.Table()

    # Use type-inference to normalize columns
    for name, c in zip(parser.headers, data_columns):
        tab.append(table.Column(0, name, c))

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output

def stream_convert(f, out, schema, **kwargs):
    try:
        f = iterdecode(f,kwargs['encoding'])
    except KeyError: pass

    parser = SchematicLineParser(schema)
    try:
        writer = UnicodeCSVWriter(out,encoding=kwargs['encoding'])
    except KeyError:
        writer = UnicodeCSVWriter(out)

    writer.writerow(parser.headers)
    
    for line in f:
        writer.writerow(parser.parse(line))


class SchematicLineParser(object):
    """Instantiated with a schema, able to return a sequence of trimmed strings representing fields given a fixed-length line."""
    def __init__(self,schema):
        self.fields = []
        schema_reader = UnicodeCSVReader(schema)

        srd = SchemaRowDecoder(row=schema_reader.next())

        for row in schema_reader:
            self.fields.append(srd(row))

    def parse(self, line):
        NAME = 0
        START = 1
        LENGTH = 2

        values = []

        for field in self.fields:
            values.append(line[field[START]:field[START] + field[LENGTH]].strip())

        return values
        
    @property
    def headers(self):
        return [x[0] for x in self.fields]

class SchemaRowDecoder(object):
    """Encapsulate the process of extracting column, start, and length columns from schema rows. Once instantiated, each time the instance is called with a row, a (column,start,length) tuple will be returned based on values in that row and the constructor kwargs."""
    PROPERTIES = ['column', 'start', 'length']
    start = None
    length = None
    column = None
    one_based = None
    def __init__(self, **kwargs):
        super(SchemaRowDecoder, self).__init__()
        for property in SchemaRowDecoder.PROPERTIES:
            try:
                setattr(self,property, kwargs[property])
            except KeyError:
                try:
                    setattr(self,property, kwargs['row'].index(property))
                except Exception:
                    raise ValueError("Property [%s] must be specified either by keyword argument or in a header row provided with the 'row' keyword argument." % (property))
        
        # verify all values set correctly
        for property in SchemaRowDecoder.PROPERTIES:
            if getattr(self,property) is None:
                raise ValueError("Property [%s] must be specified either by keyword argument or in a header row provided with the 'row' keyword argument." % (property))

    def __call__(self,row):
        """Return a tuple (column, start, length) based on this instance's parameters.
           If the first time this is called, the row's 'start' value is 1, then all 'start' 
           values including the first will be one less than in the actual input data, to adjust for
           one-based specifications.  Values for 'start' and 'length' will be cast to integers.
        """
        if self.one_based is None:
            self.one_based = (int(row[self.start]) == 1)

        if self.one_based:
            adjusted_start = int(row[self.start]) - 1
        else:
            adjusted_start = int(row[self.start])

        return (row[self.column],adjusted_start,int(row[self.length]))
