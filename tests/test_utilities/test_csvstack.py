#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvstack import CSVStack

class TestCSVStack(unittest.TestCase):
    def test_explicit_grouping(self):
        # stack two CSV files
        args = ['--groups', 'asd,sdf', '-n', 'foo', 'examples/dummy.csv', 'examples/dummy2.csv']
        output_file = six.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['foo', 'a', 'b', 'c'])
        self.assertEqual(next(reader)[0], 'asd')
        self.assertEqual(next(reader)[0], 'sdf')

    def test_filenames_grouping(self):
        # stack two CSV files
        args = ['--filenames', '-n', 'path', 'examples/dummy.csv', 'examples/dummy2.csv']
        output_file = six.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['path', 'a', 'b', 'c'])
        self.assertEqual(next(reader)[0], 'dummy.csv')
        self.assertEqual(next(reader)[0], 'dummy2.csv')

    def test_no_grouping(self):
        # stack two CSV files
        args = ['examples/dummy.csv', 'examples/dummy2.csv']
        output_file = six.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader)[0], '1')
        self.assertEqual(next(reader)[0], '1')

    def test_no_header_row(self):
        # stack two CSV files
        args = ['--no-header-row', 'examples/no_header_row.csv', 'examples/no_header_row2.csv']
        output_file = six.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader)[0], 'column1')
        self.assertEqual(next(reader)[0], '1')
        self.assertEqual(next(reader)[0], '4')
