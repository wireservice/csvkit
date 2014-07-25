#!/usr/bin/env python

from csvkit.exceptions import CSVTestException, LengthMismatchError

def join_rows(rows, joiner=' '):
    """
    Given a series of rows, return them as a single row where the inner edge cells are merged. By default joins with a single space character, but you can specify new-line, empty string, or anything else with the 'joiner' kwarg.
    """
    rows = list(rows)
    fixed_row = rows[0][:]

    for row in rows[1:]:
        if len(row) == 0:
            row = ['']
        
        fixed_row[-1] += "%s%s" % (joiner, row[0])
        fixed_row.extend(row[1:])

    return fixed_row
        
def fix_length_errors(errs, target_line_length, joiner=' '):
    """
    If possible, transform the rows backed up in the list of errors into rows of the correct length.
    If the list of errors does not yet produce a row of target_line_length, return an empty array.
    """
    if not errs:
        return []

    fixed_rows = []
    backlog = []
    
    for err in errs:
        if type(err) is not LengthMismatchError:
            return [] # give up if any are not length errors

        backlog.append(err)
        fixed_row = join_rows([err.row for err in backlog])

        if len(fixed_row) == target_line_length:
            fixed_rows.append(fixed_row)
            backlog = [] # reset
        
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
    """
    Iterate over rows of a CSV producing cleaned rows and storing error rows.
    """
    def __init__(self, reader):
        self.reader = reader
        self.column_names = next(reader)

        self.errors = []
        self.rows_joined = 0
        self.joins = 0

    def checked_rows(self):
        """
        A generator which yields rows which are ready to write to output.
        """
        line_number = self.reader.line_num
        
        for row in self.reader:
            try:
                if len(row) != len(self.column_names):
                    raise LengthMismatchError(line_number, row, len(self.column_names))

                yield row
            except LengthMismatchError as e:
                self.errors.append(e)

                joinable_row_errors = extract_joinable_row_errors(self.errors)
                
                while joinable_row_errors:
                    fixed_row = join_rows([err.row for err in joinable_row_errors], joiner=' ')

                    if len(fixed_row) < len(self.column_names):
                        break

                    if len(fixed_row) == len(self.column_names):
                        self.rows_joined += len(joinable_row_errors)
                        self.joins += 1

                        yield fixed_row
                        
                        for fixed in joinable_row_errors:
                            self.errors.remove(fixed)
                        
                        break

                    joinable_row_errors = joinable_row_errors[1:] # keep trying in case we're too long because of a straggler

            except CSVTestException as e:
                self.errors.append(e)
        
            line_number = self.reader.line_num
 
