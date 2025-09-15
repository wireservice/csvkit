"""
This module contains the Python 3 replacement for :mod:`csv`.
"""

import csv
import warnings

from agate.exceptions import FieldSizeLimitError

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']


class Reader:
    """
    A wrapper around Python 3's builtin :func:`csv.reader`.
    """
    def __init__(self, f, field_size_limit=None, line_numbers=False, header=True, **kwargs):
        self.line_numbers = line_numbers
        self.header = header

        if field_size_limit:
            csv.field_size_limit(field_size_limit)

        self.reader = csv.reader(f, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.reader)
        except csv.Error as e:
            # Terrible way to test for this exception, but there is no subclass
            if 'field larger than field limit' in str(e):
                raise FieldSizeLimitError(csv.field_size_limit(), self.line_num)
            else:
                raise e

        if not self.line_numbers:
            return row

        if self.line_numbers:
            if self.header and self.line_num == 1:
                row.insert(0, 'line_numbers')
            else:
                row.insert(0, str(self.line_num - 1 if self.header else self.line_num))

        return row

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num


class Writer:
    """
    A wrapper around Python 3's builtin :func:`csv.writer`.
    """
    def __init__(self, f, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        self.writer = csv.writer(f, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row.insert(0, 'line_number')
        else:
            row.insert(0, self.row_count)

        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = [i.replace('\r', '\n') if isinstance(i, str) else i for i in row]

        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class DictReader(csv.DictReader):
    """
    A wrapper around Python 3's builtin :class:`csv.DictReader`.
    """
    pass


class DictWriter(csv.DictWriter):
    """
    A wrapper around Python 3's builtin :class:`csv.DictWriter`.
    """
    def __init__(self, f, fieldnames, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        if self.line_numbers:
            fieldnames.insert(0, 'line_number')

        csv.DictWriter.__init__(self, f, fieldnames, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row['line_number'] = 'line_number'
        else:
            row['line_number'] = self.row_count

        self.row_count += 1

    def writerow(self, row):
        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = dict([(k, v.replace('\r', '\n')) if isinstance(v, str) else (k, v) for k, v in row.items()])

        if self.line_numbers:
            self._append_line_number(row)

        csv.DictWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Sniffer:
    """
    A functional wrapper of ``csv.Sniffer()``.
    """
    def sniff(self, sample):
        """
        A functional version of ``csv.Sniffer().sniff``, that extends the
        list of possible delimiters to include some seen in the wild.
        """
        try:
            dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
        except csv.Error as e:
            warnings.warn('Error sniffing CSV dialect: %s' % e, RuntimeWarning, stacklevel=2)
            dialect = None

        return dialect


def reader(*args, **kwargs):
    """
    A replacement for Python's :func:`csv.reader` that uses
    :class:`.csv_py3.Reader`.
    """
    return Reader(*args, **kwargs)


def writer(*args, **kwargs):
    """
    A replacement for Python's :func:`csv.writer` that uses
    :class:`.csv_py3.Writer`.
    """
    return Writer(*args, **kwargs)
