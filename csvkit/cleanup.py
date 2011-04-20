#!/usr/bin/env python

from csvkit.exceptions import CSVTestException, LengthMismatchError

def join_rows(rows,joiner=' '):
    """Given a series of rows, return them as a single row where the inner edge cells are merged. By default joins with a single space character, but you can specify new-line, empty string, or anything else with the 'joiner' kwarg."""
    rows = list(rows)
    fixed_row = rows[0][:]
    for row in rows[1:]:
        if len(row) == 0:
            row = ['']
        fixed_row[-1] += "%s%s" % (joiner,row[0])
        fixed_row.extend(row[1:])

    return fixed_row
        
def fix_length_errors(errs, target_line_length,joiner=' '):
    """If possible, transform the rows backed up in the list of errors into rows of the correct length.
       If the list of errors does not yet produce a row of target_line_length, return an empty array.
       If the joining the list of error
    """
    if not errs: return []
    fixed_rows = []
    backlog = []
    for err in errs:
        if type(err) is not LengthMismatchError: return [] # give up if any are not length errors
        backlog.append(err)
        fixed_row = join_rows([err.row for err in backlog])
        if len(fixed_row) == target_line_length:
            fixed_rows.append(fixed_row)
            backlog = [] # reset
        # elif
        
    return fixed_rows

def extract_joinable_row_errors(errs):
    joinable = []
    for err in reversed(errs):
        if type(err) is not LengthMismatchError:
            break
        if joinable and err.line_number != joinable[-1].line_number - 1:
            break
        joinable.append(err)

    joinable.reverse()    
    return joinable

class RowChecker(object):
    """When created with a reader, can yield clean rows from the reader and expose some information about what wasn't clean."""
    def __init__(self, reader):
        super(RowChecker, self).__init__()
        self.reader = reader
        self.column_names = reader.next()
        self.input_rows = 1 
        self.errs = []
        self.rows_joined = 0
        self.joins = 0
        
    def checked_rows(self):
        """A generator which yields OK rows which are ready to write to output."""
        for row in self.reader:
            self.input_rows += 1 
            line_number = self.input_rows + 1 # add one for 1-based counting

            try:
                if len(row) != len(self.column_names):
                    raise LengthMismatchError(line_number,row,len(self.column_names))
                # any other tests?
                yield row
            except LengthMismatchError, e:
                self.errs.append(e)
                # see if we can actually clean up those length mismatches
                joinable_row_errors = extract_joinable_row_errors(self.errs)
                while joinable_row_errors:
                    fixed_row = join_rows([err.row for err in joinable_row_errors], joiner=' ')
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
        
        
