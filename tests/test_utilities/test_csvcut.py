#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvcut import CSVCut
from csvkit.exceptions import ColumnIdentifierError, RequiredHeaderError

class TestCSVCut(unittest.TestCase):
    def test_simple(self):
        args = ['-c', '1,3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_unicode(self):
        args = ['-c', '1,3', 'examples/test_utf8.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])
        self.assertEqual(next(reader), ['4', u'ʤ'])

    def test_names(self):
        args = ['-n', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())

        self.assertEqual(next(input_file), '  1: a\n')
        self.assertEqual(next(input_file), '  2: b\n')
        self.assertEqual(next(input_file), '  3: c\n')

    def test_with_gzip(self):
        args = ['-c', '1,3', 'examples/dummy.csv.gz']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_with_bzip2(self):
        args = ['-c', '1,3', 'examples/dummy.csv.bz2']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_exclude(self):
        args = ['-C', '1,3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['b'])
        self.assertEqual(next(reader), ['2'])

    def test_include_and_exclude(self):
        args = ['-c', '1,3', '-C', '3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a'])
        self.assertEqual(next(reader), ['1'])

    def test_invalid_column(self):
        args = ['-c', '0', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        self.assertRaises(ColumnIdentifierError, utility.main)

    def test_invalid_options(self):
        args = ['-n', '--no-header-row', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        self.assertRaises(RequiredHeaderError, utility.main)

    def test_no_header_row(self):
        args = ['-c', '2', '--no-header-row', 'examples/no_header_row.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['column2'])
        self.assertEqual(next(reader), ['2'])

