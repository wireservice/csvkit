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

class FixedWidthReader(object):
    """Given a fixed-width file and a schema file, produce an analog to a csv reader that yields a row 
    of strings for each line in the fixed-width file, preceded with a row of headers as provided in the schema.  (This might be problematic if fixed-width-files ever have header rows also, but I haven't seen that.)
    
    The schema_file should be in CSV format with a header row which has columns 'column', 'start', and 'length'. (Other columns will be ignored.)  Values in the 'start' column are assumed to be "zero-based" unless the first value is "1" in which case all values are assumed to be "one-based."
    """
    def __init__(self, f, schema_file):
        super(FixedWidthReader, self).__init__()
        self.parser = SchematicLineParser(schema_file)
        self.file = f
        self.header = True

    def __iter__(self):
        return self
        
    def next(self):
        if self.header:
            self.header = False
            return self.parser.headers
        return self.parser.parse(self.file.next())
    

def stream_convert(f, out, schema_file, **kwargs):
    try:
        f = iterdecode(f,kwargs['encoding'])
    except KeyError: pass

    try:
        writer = UnicodeCSVWriter(out,encoding=kwargs['encoding'])
    except KeyError:
        writer = UnicodeCSVWriter(out)

    fwr = FixedWidthReader(f, schema_file)

    writer.writerows(fwr)
    

class SchematicLineParser(object):
    """Instantiated with a schema, able to return a sequence of trimmed strings representing fields given a fixed-length line. Flexible about where the columns are, as long as they are headed with the literal names 'column', 'start', and 'length'.  
    """
    NAME = 0
    START = 1
    LENGTH = 2
    def __init__(self,schema):
        self.fields = []
        schema_reader = UnicodeCSVReader(schema)

        srd = SchemaRowDecoder(row=schema_reader.next())

        for row in schema_reader:
            self.fields.append(srd(row))

    def parse(self, line):

        values = []

        for field in self.fields:
            values.append(line[field[self.START]:field[self.START] + field[self.LENGTH]].strip())

        return values
        
    @property
    def headers(self):
        return [x[self.NAME] for x in self.fields]

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
