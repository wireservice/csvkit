import csv
import sys


class CSVTestException(Exception):
    """Superclass for all row-test-failed exceptions. 
       All must have a line number, the problematic row, and a text explanation."""
    def __init__(self, line_number, row, msg):
        super(CSVTestException, self).__init__()
        self.msg = msg
        self.line_number = line_number
        self.row = row
        
class LengthMismatch(CSVTestException):
    """Encapsulate information about a row which as the wrong length."""
    def __init__(self, line_number, row, expected_length):
        msg = "Expected length [%i], got length [%i]" % (expected_length, len(row))
        super(LengthMismatch, self).__init__(line_number, row, msg)
    
    @property
    def length(self):
        return len(self.row)

def join_rows(rows):
    """Given a series of rows, return them as a single row where the inner edge cells are merged"""
    rows = list(rows)
    fixed_row = rows[0][:-1]
    merged = [rows[0][-1]]
    for row in rows[1:-1]:
        merged.extend(row)

    if len(rows) > 1 and len(rows[-1]) > 0:
        try:    
            merged.append(rows[-1][0])
        except IndexError:
            from pprint import pprint
            print "index error?"
            pprint(rows)

    fixed_row.append('\n'.join(merged))
    fixed_row.extend(rows[-1][1:])
    return fixed_row

def fix_length_errors(errs, target_line_length):
    """If possible, transform the rows backed up in the list of errors into rows of the correct length.
       If the list of errors does not yet produce a row of target_line_length, return an empty array.
       If the joining the list of error
    """
    if not errs: return []
    fixed_rows = []
    backlog = []
    for err in errs:
        if type(err) is not LengthMismatch: return [] # give up if any are not length errors
        backlog.append(err)
        fixed_row = join_rows([err.row for err in backlog])
        if len(fixed_row) == target_line_length:
            fixed_rows.append(fixed_row)
            backlog = [] # reset
        # elif
        
    return fixed_rows

def format_error_row(e):
    """Format a row for """
    err_row = [e.line_number, e.msg]
    err_row.extend(row)
    return err_row

def extract_joinable_row_errors(errs):
    joinable = []
    for err in reversed(errs):
        if type(err) is not LengthMismatch:
            break
        if joinable and err.line_number != joinable[-1].line_number - 1:
            break
        joinable.append(err)

    joinable.reverse()    
    return joinable

class RowChecker(object):
    """docstring for RowChecker"""
    def __init__(self, reader):
        super(RowChecker, self).__init__()
        self.reader = reader
        self.column_names = reader.next()
        self.errs = []
        self.rows_joined = 0
        self.joins = 0
        
    def checked_rows(self):
        """A generator which yields OK rows which are ready to write to output."""
        for i,row in enumerate(self.reader):
            line_number = i + 2 # adjust for header row, plus add one for 1-based counting
            try:
                if len(row) != len(self.column_names):
                    raise LengthMismatch(line_number,row,len(self.column_names))

                yield row
            except LengthMismatch, e:
                self.errs.append(e)
                joinable_row_errors = extract_joinable_row_errors(self.errs)
                while joinable_row_errors:
                    fixed_row = join_rows(err.row for err in joinable_row_errors)
                    if len(fixed_row) < len(self.column_names): break
                    if len(fixed_row) == len(self.column_names):
                        self.rows_joined += len(joinable_row_errors)
                        self.joins += 1
                        yield fixed_row
                        for fixed in joinable_row_errors:
                            self.errs.remove(fixed)
                        break
                    joinable_row_errors = joinable_row_errors[1:] # keep trying in case we're too long because of a straggler

            except CSVTestException, e:
                self.errs.append(e)
        
        
