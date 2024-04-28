#!/usr/bin/env python

from csvkit.exceptions import CSVTestException, LengthMismatchError


def join_rows(rows, joiner=' '):
    """
    Given a series of rows, return them as a single row where the inner edge cells are merged.

    :param joiner:
        The separator between cells, a single space by default.
    """
    rows = list(rows)
    fixed_row = rows[0][:]

    for row in rows[1:]:
        if len(row) == 0:
            row = ['']

        fixed_row[-1] += f"{joiner}{row[0]}"
        fixed_row.extend(row[1:])

    return fixed_row


class RowChecker:
    """
    Iterate over rows of a CSV producing cleaned rows and storing error rows.
    """

    def __init__(self, reader, header_normalize_space=False):
        self.reader = reader
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
        line_number = self.reader.line_num
        joinable_row_errors = []

        for row in self.reader:
            try:
                if len(row) != length:
                    raise LengthMismatchError(line_number, row, length)

                yield row

                # Don't join rows across valid rows.
                joinable_row_errors = []
            except LengthMismatchError as e:
                self.errors.append(e)

                # Don't join with long rows.
                if len(row) > length:
                    joinable_row_errors = []
                else:
                    joinable_row_errors.append(e)

                    while joinable_row_errors:
                        fixed_row = join_rows([error.row for error in joinable_row_errors], joiner=' ')

                        if len(fixed_row) < length:
                            break

                        if len(fixed_row) == length:
                            yield fixed_row

                            for fixed in joinable_row_errors:
                                joinable_row_errors.remove(fixed)
                                self.errors.remove(fixed)

                            break

                        # keep trying in case we're too long because of a straggler
                        joinable_row_errors = joinable_row_errors[1:]

            except CSVTestException as e:
                self.errors.append(e)

                # Don't join rows across other errors.
                joinable_row_errors = []

            line_number = self.reader.line_num
