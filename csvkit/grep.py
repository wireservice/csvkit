class FilteringCSVReader(object):
    """Given any row iterator, only return rows which pass the filter.
       If 'header' is False, then all rows must pass the filter; by default, the 
       first row will be passed through untested.
    """
    def __init__(self, reader, header=True, **kwargs):
        super(FilteringCSVReader, self).__init__()
        self.reader = reader
        self.header = header
        self.regex = None
        self.pattern = None
        
        try:
            self.column_ids = kwargs['column_ids']
        except KeyError: # for now, if no column IDs are passed, then all columns must pass
            self.column_ids = None
        try:
            self.regex = kwargs['regex']
        except KeyError:
            try:
                self.pattern = kwargs['pattern']
            except KeyError: # for now, if neither regex or pattern are provided, then each specified column will be tested for boolean truth.
                pass

    def __iter__(self):
        return self
        
    def next(self):
        if self.header:
            self.header = False
            return self.reader.next()
        while True:
            row = self.reader.next()
            if self.passes(row):
                return row
        raise StopIteration()
        
    def passes(self,row):
        if self.column_ids:
            newrow = []
            for c in self.column_ids:
                newrow.append(row[c])
            row = newrow
        for value in row:
            if not self._value_passes(value):
                return False
        return True
        
    def _value_passes(self, value):
        if self.regex:
            return self.regex.match(value)
        if self.pattern:
            return value in self.pattern
        return bool(value)

