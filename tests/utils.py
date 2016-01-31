#!/usr/bin/env python

import sys
from contextlib import contextmanager

import agate
import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.exceptions import ColumnIdentifierError, RequiredHeaderError


@contextmanager
def stderr_as_stdout():
    temp = sys.stderr
    sys.stderr = sys.stdout
    yield
    sys.stderr = temp


@contextmanager
def stdin_as_string(str):
    temp = sys.stdin
    sys.stdin = str
    yield
    sys.stdin = temp


class CSVKitTestCase(unittest.TestCase):
    def get_output(self, args):
        output_file = six.StringIO()

        utility = self.Utility(args, output_file)
        utility.main()

        return six.StringIO(output_file.getvalue())

    def assertRows(self, args, rows):
        reader = agate.reader(self.get_output(args))
        for row in rows:
            self.assertEqual(next(reader), row)


class NamesTests(object):
    def test_names(self):
        output = self.get_output(['-n', 'examples/dummy.csv'])

        self.assertEqual(next(output), '  1: a\n')
        self.assertEqual(next(output), '  2: b\n')
        self.assertEqual(next(output), '  3: c\n')

    def test_invalid_options(self):
        args = ['-n', '--no-header-row', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = self.Utility(args, output_file)
        self.assertRaises(RequiredHeaderError, utility.main)


class ColumnsTests(object):
    def test_invalid_column(self):
        args = getattr(self, 'columns_args', []) + ['-c', '0', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = self.Utility(args, output_file)
        self.assertRaises(ColumnIdentifierError, utility.main)
