#!/usr/bin/env python

class ColumnIdentifierError(Exception):
    """
    Exception raised when the user supplies an invalid column identifier.
    """
    def __init__(self, msg):
        self.msg = msg

class XLSDataError(Exception):
    """
    Exception raised when there is a problem converting XLS data.
    """
    def __init__(self, msg):
        self.msg = msg

class CSVTestException(Exception):
    """
    Superclass for all row-test-failed exceptions. 
    All must have a line number, the problematic row, and a text explanation.
    """
    def __init__(self, line_number, row, msg):
        super(CSVTestException, self).__init__()
        self.msg = msg
        self.line_number = line_number
        self.row = row
        
class LengthMismatchError(CSVTestException):
    """
    Encapsulate information about a row which as the wrong length.
    """
    def __init__(self, line_number, row, expected_length):
        msg = "Expected %i columns, found %i columns" % (expected_length, len(row))
        super(LengthMismatchError, self).__init__(line_number, row, msg)
    
    @property
    def length(self):
        return len(self.row)

