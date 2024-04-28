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
        header_normalize_space=False,
        join_short_rows=False,
        separator='\n',
        fill_short_rows=False,
        fillvalue=None,
        empty_columns=False,
        zero_based=False,
    ):
        self.reader = reader
        self.join_short_rows = join_short_rows
        self.separator = separator
        self.fill_short_rows = fill_short_rows
        self.fillvalue = fillvalue
        self.empty_columns = empty_columns
        self.zero_based = zero_based

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

        for row in self.reader:
            line_number = self.reader.line_num - 1
            row_count += 1
            len_row = len(row)

            if self.empty_columns:
                for i, value in enumerate(row):
                    if value == '':
                        empty_counts[i] += 1

            if len_row == len_column_names:
                yield row

                if self.join_short_rows:
                    # Don't join rows across valid rows.
                    joinable_row_errors = []

                continue

            if self.fill_short_rows and len_row < len_column_names:
                yield row + [self.fillvalue] * (len_column_names - len_row)

                continue

            length_error = Error(line_number, row, f'Expected {len_column_names} columns, found {len_row} columns')

            self.errors.append(length_error)

            if self.join_short_rows:
                if len_row > len_column_names:
                    # Don't join with long rows.
                    joinable_row_errors = []
                    continue

                joinable_row_errors.append(length_error)
                if len(joinable_row_errors) == 1:
                    continue

                while joinable_row_errors:
                    fixed_row = join_rows([error.row for error in joinable_row_errors], separator=self.separator)

                    if len(fixed_row) < len_column_names:
                        break

                    if len(fixed_row) == len_column_names:
                        yield fixed_row

                        for fixed in joinable_row_errors:
                            self.errors.remove(fixed)

                        joinable_row_errors = []
                        break

                    # keep trying in case we're too long because of a straggler
                    joinable_row_errors = joinable_row_errors[1:]

        if row_count:
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
