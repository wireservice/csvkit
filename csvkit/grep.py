import re

class FilteringCSVReader(object):
    """Given any row iterator, only return rows which pass the filter.
       If 'header' is False, then all rows must pass the filter; by default, the 
       first row will be passed through untested.
       
       The value of patterns may be either a sequence or a dictionary.  Items in the sequence and values in the 
       dictionary may be strings, regular expressions, or functions.  For each row in the wrapped iterator, 
       these values will be used as tests, and the row will only be yielded by the filter if all values pass 
       their corresponding tests.  This behavior can be toggled so that all rows which pass any of the tests
       will be yielded by specifying "any=True" in the constructor.
       
       Empty values (the blank string or None) not be tested; the value in that position will not affect whether
       or not the filterint reader yields a prospective row.  To test for explicitly blank, use a regular
       expression such as "^$" or "^\s*$"
       
       If patterns is a dictionary, the keys should be integers identifying indices in the input rows. (It might 
       be that this would all work with a dictionary iterator and a looser set of keys, but that's not 
       officially supported.)  If patterns is a sequence, then it is assumed that they will be applied to the 
       equivalently positioned values in the test rows.
       
       By specifying 'inverse=True', only rows which do not match the patterns will be passed by the filter.
    """
    def __init__(self, reader, patterns, header=True, any=False, inverse=False):
        super(FilteringCSVReader, self).__init__()
        self.reader = reader
        self.patterns = standardize_patterns(patterns)
        self.header = header
        self.any = any
        self.inverse = inverse

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
        for idx, test in self.patterns.items():
            if self.any and test(row[idx]):
                return not self.inverse # "True"
            if not self.any and not test(row[idx]):
                return self.inverse # "False"

        return not self.inverse # "True"
        
def standardize_patterns(patterns):
    """Given patterns in any of the permitted input forms, return a dict whose keys 
       are row indices and whose values are functions which return a boolean value whether the value passes."""

    try:
        return dict((k,functionalize(v)) for k,v in patterns.items() if v)
    except AttributeError:
       return dict((i,functionalize(x)) for i,x in enumerate(patterns))

def functionalize(obj):
    if hasattr(obj, '__call__'): return obj
    if hasattr(obj, 'match'): return regex_caller(obj)
    return regex_caller(re.compile(obj))

class regex_caller(object):
    def __init__(self, pattern):
        self.pattern = pattern
        
    def __call__(self, arg):
        return self.pattern.match(arg)        