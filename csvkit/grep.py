#!/usr/bin/env python

import re

class FilteringCSVReader(object):
    """
    Given any row iterator, only return rows which pass the filter.
    If 'header' is False, then all rows must pass the filter; by default, the first row will be passed
    through untested.
       
    The value of patterns may be either a sequence or a dictionary.  Items in the sequence and values in the 
    dictionary may be strings, regular expressions, or functions.  For each row in the wrapped iterator, 
    these values will be used as tests, and the row will only be yielded by the filter if all values pass 
    their corresponding tests.  This behavior can be toggled so that all rows which pass any of the tests
    will be yielded by specifying "any_match=True" in the constructor.
       
    Empty values (the blank string or None) not be tested; the value in that position will not affect whether
    or not the filtering reader yields a prospective row.  To test for explicitly blank, use a regular
    expression such as "^$" or "^\s*$"
       
    If patterns is a dictionary, the keys should be integers identifying indices in the input rows. (It might 
    be that this would all work with a dictionary iterator and a looser set of keys, but that's not 
    officially supported.)  If patterns is a sequence, then it is assumed that they will be applied to the 
    equivalently positioned values in the test rows.
       
    By specifying 'inverse=True', only rows which do not match the patterns will be passed by the filter.
    """
    def __init__(self, reader, patterns, header=True, any_match=False, inverse=False):
        super(FilteringCSVReader, self).__init__()

        self.reader = reader
        self.patterns = standardize_patterns(patterns)
        self.header = header
        self.any_match = any_match
        self.inverse = inverse

    def __iter__(self):
        return self
        
    def next(self):
        if self.header:
            self.header = False
            return self.reader.next()

        while True:
            row = self.reader.next()
            if self.test_row(row):
                return row

        raise StopIteration()
        
    def test_row(self, row):
        for idx, test in self.patterns.items():
            if self.any_match and test(row[idx]):
                return not self.inverse # True

            if not self.any_match and not test(row[idx]):
                return self.inverse # False

        return not self.inverse # True
        
def standardize_patterns(patterns):
    """
    Given patterns in any of the permitted input forms, return a dict whose keys 
    are row indices and whose values are functions which return a boolean value whether the value passes.
    """
    try:
        # Dictionary of patterns
        return dict((k, pattern_as_function(v)) for k, v in patterns.items() if v)
    except AttributeError:
        # Sequence of patterns
        return dict((i, pattern_as_function(x)) for i, x in enumerate(patterns))

def pattern_as_function(obj):
    # obj is function
    if hasattr(obj, '__call__'):
        return obj
    
    # obj is regex object
    if hasattr(obj, 'match'):
        return regex_callable(obj)

    # obj is string
    return lambda x: obj in x

class regex_callable(object):
    def __init__(self, pattern):
        self.pattern = pattern
        
    def __call__(self, arg):
        return self.pattern.match(arg)        
