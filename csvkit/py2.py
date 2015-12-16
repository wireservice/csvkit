#!/usr/bin/env python

"""
Python2-specific classes.
"""

import six

from csvkit import unicsv

class CSVKitReader(unicsv.UnicodeCSVReader):
    """
    A unicode-aware CSV reader.
    """
    pass 

class CSVKitWriter(unicsv.UnicodeCSVWriter):
    """
    A unicode-aware CSV writer.
    """
    def __init__(self, f, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        unicsv.UnicodeCSVWriter.__init__(self, f, encoding, **kwargs)

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
        row = [i.replace('\r', '\n') if isinstance(i, six.string_types) else i for i in row]

        unicsv.UnicodeCSVWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class CSVKitDictReader(unicsv.UnicodeCSVDictReader):
    """
    A unicode-aware CSV DictReader.
    """
    pass

class CSVKitDictWriter(unicsv.UnicodeCSVDictWriter):
    """
    A unicode-aware CSV DictWriter.
    """
    def __init__(self, f, fieldnames, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        unicsv.UnicodeCSVDictWriter.__init__(self, f, fieldnames, encoding=encoding, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row['line_number'] = 0
        else:
            row['line_number'] = self.row_count
            
        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = dict([(k, v.replace('\r', '\n')) if isinstance(v, basestring) else (k, v) for k, v in row.items()])

        unicsv.UnicodeCSVDictWriter.writerow(self, row)

    # Modifying writerows to catch UnicodeEncodeError
    def writerows(self, rowdicts):
        # Iterating every row one by one
        for rowdict in rowdicts:
            # Accessing key value pair in a rowdict
            for key, value in rowdict.items():
                # Including the value in try block
                try:
                    # Decoding the utf-8 into target ascii with ignore parameter
                    value.decode('ascii').encode('ascii', 'ignore')
                except UnicodeEncodeError:
                    # Replacing the string with empty value if any Encoding error occurs
                    rowdict[key] = ''
                except AttributeError:
                    continue

            writer.writerow(rowdict)
def reader(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.reader` that leverages :class:`csvkit.py2.CSVKitReader`.
    """
    return CSVKitReader(*args, **kwargs)

def writer(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.writer` that leverages :class:`csvkit.py2.CSVKitWriter`.
    """
    return CSVKitWriter(*args, **kwargs)

