#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import re
# noinspection PyUnresolvedReferences
import math
# noinspection PyUnresolvedReferences
import random
# noinspection PyUnresolvedReferences
import collections


class ScriptCSVReader(object):
    """
    Given any row iterator returns header and rows after evaluation series of scripts on them.
    Each script produces a value which is concatenated as another column in csv.
    """
    returned_header = False
    column_names = None

    def __init__(self, reader, scripts, zero_based=False):
        super(ScriptCSVReader, self).__init__()
        self.zero_based = zero_based
        self.reader = reader
        self.scripts = scripts
        self.column_names = reader.next()

    def __iter__(self):
        return self

    def next(self):
        if self.column_names and not self.returned_header:
            self.returned_header = True
            return self.column_names + map(lambda script: script[0], self.scripts)

        while True:
            row = self.reader.next()
            return row + list(run_scripts(self.scripts, row, self.column_names, self.zero_based))

        raise StopIteration()


def run_scripts(scripts, row, column_names, zero_based):
    for script in scripts:
        yield eval(script[1], globals(), {
            'c': row if zero_based else dict((i + 1, r) for i, r in enumerate(row)),
            'ch': dict(zip(column_names, row))
        }
        )

