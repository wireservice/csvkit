#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader, UnicodeCSVWriter

class CSVKitReader(UnicodeCSVReader):
    """
    A unicode-aware CSV reader with some additional features.
    """
    pass

class CSVKitWriter(UnicodeCSVWriter):
    """
    A unicode-aware CSV writer with some additional features.
    """
    def __init__(self, f, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers
        UnicodeCSVWriter.__init__(self, f, encoding, **kwargs)

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

        UnicodeCSVWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

