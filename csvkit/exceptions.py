#!/usr/bin/env python

class CustomException(Exception):
    """
    A base exception that handles pretty-printing.
    """
    def __init__(self, msg):
        self.msg = msg

    def __unicode__(self):
        return self.msg

    def __str__(self):
        return self.msg

class FieldSizeLimitError(CustomException):
    """
    Exception raised when a field in the CSV file exceeds the default max
    or one provided by the user.
    """
    def __init__(self, limit):
        self.msg = 'CSV contains fields longer than maximum length of %i characters. Try raising the maximum with the --maxfieldsize flag.' % limit

class ColumnIdentifierError(CustomException):
    """
    Exception raised when the user supplies an invalid column identifier.
    """
    pass

class XLSDataError(CustomException):
    """
    Exception raised when there is a problem converting XLS data.
    """
    pass

class CSVTestException(CustomException):
    """
    Superclass for all row-test-failed exceptions. 
    All must have a line number, the problematic row, and a text explanation.
    """
    def __init__(self, line_number, row, msg):
        super(CSVTestException, self).__init__(msg)
        self.line_number = line_number
        self.row = row
        
class LengthMismatchError(CSVTestException):
    """
    Encapsulate information about a row which as the wrong length.
    """
    def __init__(self, line_number, row, expected_length):
        msg = 'Expected %i columns, found %i columns' % (expected_length, len(row))
        super(LengthMismatchError, self).__init__(line_number, row, msg)
    
    @property
    def length(self):
        return len(self.row)

class CSVJSONException(CustomException):
    """
    Exception raised when there is a problem converting data to CSV.
    """
    pass

class NonUniqueKeyColumnException(CSVJSONException):
    pass

class InvalidValueForTypeException(CustomException):
    """
    Exception raised when a value can not be normalized to a specified type.
    """
    def __init__(self, index, value, normal_type):
        self.index = index
        self.value = value
        self.normal_type = normal_type
        msg = 'Unable to convert "%s" to type %s (at index %i)' % (value, normal_type, index)
        super(InvalidValueForTypeException, self).__init__(msg)

class InvalidValueForTypeListException(CustomException):
    """
    Exception raised when one or more InvalidValueForTypeException
    has been raised while accumulating errors.
    """
    def __init__(self, errors):
        self.errors = errors
        msg = 'Encountered errors converting values in %i columns' % len(errors)
        super(InvalidValueForTypeListException, self).__init__(msg)

