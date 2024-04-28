#!/usr/bin/env python

from csvkit.exceptions import CSVTestException, LengthMismatchError


def join_rows(rows, separator):
    """
    Given a series of rows, return them as a single row where the inner edge cells are merged.

    :param separator:
        The string with which to join the cells.
    """
    rows = list(rows)
    fixed_row = rows[0][:]

    for row in rows[1:]:
        if len(row) == 0:
            row = ['']

        fixed_row[-1] += f"{separator}{row[0]}"
        fixed_row.extend(row[1:])

    return fixed_row


class RowChecker:
    """
    Iterate over rows of a CSV producing cleaned rows and storing error rows.
    """

    def __init__(self, reader, header_normalize_space=False, join_short_rows=False, separator='\n'):
        self.reader = reader
        self.join_short_rows = join_short_rows
        self.separator = separator

        try:
            self.column_names = next(reader)
            if header_normalize_space:
                self.column_names = [' '.join(column_name.split()) for column_name in self.column_names]
        except StopIteration:
            self.column_names = []

        self.errors = []

    def checked_rows(self):
        """
        A generator which yields rows which are ready to write to output.
        """
        length = len(self.column_names)
        joinable_row_errors = []

        for row in self.reader:
            if len(row) == length:
                yield row

                # Don't join rows across valid rows.
                joinable_row_errors = []
                continue

            length_mismatch_error = LengthMismatchError(self.reader.line_num - 1, row, length)

            self.errors.append(length_mismatch_error)

            if len(row) > length:
                # Don't join with long rows.
                joinable_row_errors = []
                continue

            if not self.join_short_rows:
                continue

            joinable_row_errors.append(length_mismatch_error)
            if len(joinable_row_errors) == 1:
                continue

            while joinable_row_errors:
                fixed_row = join_rows([error.row for error in joinable_row_errors], separator=self.separator)

                if len(fixed_row) < length:
                    break

                if len(fixed_row) == length:
                    yield fixed_row

                    for fixed in joinable_row_errors:
                        self.errors.remove(fixed)

                    joinable_row_errors = []
                    break

                # keep trying in case we're too long because of a straggler
                joinable_row_errors = joinable_row_errors[1:]
