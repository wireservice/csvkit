"""
This module contains the XLSX extension to :class:`Table <agate.table.Table>`.
"""

import datetime
from collections import OrderedDict

import agate
import openpyxl

NULL_TIME = datetime.time(0, 0, 0)


def from_xlsx(cls, path, sheet=None, skip_lines=0, header=True, read_only=True,
              reset_dimensions=None, row_limit=None, **kwargs):
    """
    Parse an XLSX file.

    :param path:
        Path to an XLSX file to load or a file-like object for one.
    :param sheet:
        The names or integer indices of the worksheets to load. If not specified
        then the "active" sheet will be used.
    :param skip_lines:
        The number of rows to skip from the top of the sheet.
    :param header:
        If :code:`True`, the first row is assumed to contain column names.
    :param read_only:
        If :code:`True`, the XLSX file is opened in read-only mode, to reduce
        memory consumption.
    :param reset_dimensions:
        If :code:`True`, do not trust the dimensions in the file's properties,
        and recalculate them based on the data in the file.
    :param row_limit:
        Limit how many rows of data will be read.
    """
    if not isinstance(skip_lines, int):
        raise ValueError('skip_lines argument must be an int')

    if hasattr(path, 'read'):
        f = path
    else:
        f = open(path, 'rb')

    book = openpyxl.load_workbook(f, read_only=read_only, data_only=True)

    multiple = agate.utils.issequence(sheet)
    if multiple:
        sheets = sheet
    else:
        sheets = [sheet]

    tables = OrderedDict()

    for i, sheet in enumerate(sheets):
        if isinstance(sheet, str):
            try:
                sheet = book[sheet]
            except KeyError:
                f.close()
                raise
        elif isinstance(sheet, int):
            try:
                sheet = book.worksheets[sheet]
            except IndexError:
                f.close()
                raise
        else:
            sheet = book.active

        column_names = None
        offset = 0
        rows = []

        if (
            read_only
            and (reset_dimensions or (reset_dimensions is None and sheet.max_column == 1 and sheet.max_row == 1))
        ):
            try:
                sheet.reset_dimensions()
                sheet.calculate_dimension(force=True)
            # https://foss.heptapod.net/openpyxl/openpyxl/-/issues/2111
            except UnboundLocalError:
                pass

        if header:
            sheet_header = sheet.iter_rows(min_row=1 + skip_lines, max_row=1 + skip_lines)
            column_names = [None if c.value is None else str(c.value) for row in sheet_header for c in row]
            offset = 1

        if row_limit is None:
            sheet_rows = sheet.iter_rows(min_row=1 + skip_lines + offset)
        else:
            sheet_rows = sheet.iter_rows(min_row=1 + skip_lines + offset, max_row=1 + skip_lines + offset + row_limit)

        for i, row in enumerate(sheet_rows):
            values = []

            for c in row:
                value = c.value

                if value.__class__ is datetime.datetime:
                    # Handle default XLSX date as 00:00 time
                    if value.date() == datetime.date(1904, 1, 1) and not has_date_elements(c):
                        value = value.time()

                        value = normalize_datetime(value)
                    elif value.time() == NULL_TIME:
                        value = value.date()
                    else:
                        value = normalize_datetime(value)

                values.append(value)

            rows.append(values)

        if 'column_names' in kwargs:
            if not header:
                column_names = kwargs['column_names']
            del kwargs['column_names']

        tables[sheet.title] = agate.Table(rows, column_names, **kwargs)

    f.close()

    if multiple:
        return agate.MappedSequence(tables.values(), tables.keys())
    return tables.popitem()[1]


def normalize_datetime(dt):
    if dt.microsecond == 0:
        return dt

    ms = dt.microsecond

    if ms < 1000:
        return dt.replace(microsecond=0)
    if ms > 999000:
        return dt.replace(microsecond=0) + datetime.timedelta(seconds=1)

    return dt


def has_date_elements(cell):
    """
    Try to use formatting to determine if a cell contains only time info.

    See: http://office.microsoft.com/en-us/excel-help/number-format-codes-HP005198679.aspx
    """
    return 'd' in cell.number_format or 'y' in cell.number_format


agate.Table.from_xlsx = classmethod(from_xlsx)
