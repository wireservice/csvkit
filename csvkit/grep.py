#!/usr/bin/env python

import six

from csvkit.exceptions import ColumnIdentifierError


class FilteringCSVReader(six.Iterator):
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

    If patterns is a dictionary, the keys can be integers identifying indices in the input rows, or, if 'header'
    is True (as it is by default), they can be strings matching column names in the first row of the reader.

    If patterns is a sequence, then it is assumed that they will be applied to the
    equivalently positioned values in the test rows.

    By specifying 'inverse=True', only rows which do not match the patterns will be passed by the filter. The header,
    if there is one, will always be returned regardless of the value for 'inverse'.
    """
    returned_header = False
    column_names = None

    def __init__(self, reader, patterns, header=True, any_match=False, inverse=False):
        super(FilteringCSVReader, self).__init__()

        self.reader = reader
        self.header = header

        if self.header:
            self.column_names = next(reader)

        self.any_match = any_match
        self.inverse = inverse
        self.patterns = standardize_patterns(self.column_names, patterns)

    def __iter__(self):
        return self

    def __next__(self):
        if self.column_names and not self.returned_header:
            self.returned_header = True
            return self.column_names

        while True:
            row = next(self.reader)

            if self.test_row(row):
                return row

        raise StopIteration()

    def test_row(self, row):
        for idx, test in self.patterns.items():
            try:
                value = row[idx]
            except IndexError:
                value = ''
            result = test(value)
            if self.any_match:
                if result:
                    return not self.inverse  # True
            else:
                if not result:
                    return self.inverse  # False

        if self.any_match:
            return self.inverse  # False
        else:
            return not self.inverse  # True


def standardize_patterns(column_names, patterns):
    """
    Given patterns in any of the permitted input forms, return a dict whose keys
    are column indices and whose values are functions which return a boolean value whether the value passes.
    If patterns is a dictionary and any of its keys are values in column_names, the returned dictionary will
    have those keys replaced with the integer position of that value in column_names
    """
    try:
        # Dictionary of patterns
        patterns = dict((k, pattern_as_function(v)) for k, v in patterns.items() if v)
        if not column_names:
            return patterns
        p2 = {}
        for k in patterns:
            if k in column_names:
                idx = column_names.index(k)
                if idx in patterns:
                    raise ColumnIdentifierError("Column %s has index %i which already has a pattern." % (k, idx))
                p2[idx] = patterns[k]
            else:
                p2[k] = patterns[k]
        return p2
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
        return self.pattern.search(arg)
