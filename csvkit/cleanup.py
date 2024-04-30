#!/usr/bin/env python
from dataclasses import dataclass


@dataclass
class Error:
    line_number: int
    row: int
    msg: str


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

    def __init__(
        self,
        reader,
        # Checks
        length_mismatch=False,
        empty_columns=False,
        # Fixes
        header_normalize_space=False,
        join_short_rows=False,
        separator='\n',
        fill_short_rows=False,
        fillvalue=None,
        # Other
        zero_based=False,
        omit_error_rows=False,
    ):
        self.reader = reader
        # Checks
        self.length_mismatch = length_mismatch
        self.empty_columns = empty_columns
        # Fixes
        self.join_short_rows = join_short_rows
        self.separator = separator
        self.fill_short_rows = fill_short_rows
        self.fillvalue = fillvalue
        # Other
        self.zero_based = zero_based
        self.omit_error_rows = omit_error_rows

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
        len_column_names = len(self.column_names)
        joinable_row_errors = []

        row_count = 0
        empty_counts = [0 for _ in range(len_column_names)]

        # Row-level checks and fixes.
        for row in self.reader:
            line_number = self.reader.line_num - 1
            row_count += 1

            # Potential errors

            length_error = Error(line_number, row, f'Expected {len_column_names} columns, found {len(row)} columns')

            # Fixes (replace `row`)

            if self.fill_short_rows:
                if len(row) < len_column_names:
                    row += [self.fillvalue] * (len_column_names - len(row))
            # --join-error-rows and --fill-error-rows are mutually exclusive.
            elif self.join_short_rows:
                # Don't join short rows across valid rows or with long rows.
                if len(row) >= len_column_names:
                    joinable_row_errors = []
                else:
                    joinable_row_errors.append(length_error)

                    if len(joinable_row_errors) > 1:
                        while joinable_row_errors:
                            fixed_row = join_rows([e.row for e in joinable_row_errors], separator=self.separator)

                            if len(fixed_row) < len_column_names:
                                # Stop trying, if we are too short.
                                break

                            if len(fixed_row) == len_column_names:
                                row = fixed_row

                                # Remove the errors that are now fixed.
                                if self.length_mismatch:
                                    for fixed in joinable_row_errors:
                                        self.errors.remove(fixed)

                                joinable_row_errors = []
                                break

                            # Keep trying, if we are too long.
                            joinable_row_errors = joinable_row_errors[1:]

            # Standard error

            if self.length_mismatch:
                if len(row) != len_column_names:
                    self.errors.append(length_error)

            # Increment the number of empty cells for each column.
            if self.empty_columns:
                for i in range(len_column_names):
                    if i >= len(row) or row[i] == '':
                        empty_counts[i] += 1

            # Standard output

            if not self.omit_error_rows or len(row) == len_column_names:
                yield row

        # File-level checks and fixes.

        if row_count:  # Don't report all columns as empty if there are no data rows.
            if empty_columns := [i for i, count in enumerate(empty_counts) if count == row_count]:
                offset = 0 if self.zero_based else 1
                self.errors.append(
                    Error(
                        1,
                        ["" for _ in range(len_column_names)],
                        f"Empty columns named {', '.join(repr(self.column_names[i]) for i in empty_columns)}! "
                        f"Try: csvcut -C {','.join(str(i + offset) for i in empty_columns)}",
                    )
                )
