#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import agate
import six

try:
    import unittest2 as unittest
    from mock import patch
except ImportError:
    import unittest
    from unittest.mock import patch

from csvkit.utilities.csvcut import CSVCut, launch_new_instance
from tests import ColumnsTests, NamesTests


class TestCSVCut(unittest.TestCase, ColumnsTests, NamesTests):
    Utility = CSVCut

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvcut', 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        args = ['-c', '1,3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_unicode(self):
        args = ['-c', '1,3', 'examples/test_utf8.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['foo', 'baz'])
        self.assertEqual(next(reader), ['1', '3'])
        self.assertEqual(next(reader), ['4', u'ʤ'])

    def test_with_gzip(self):
        args = ['-c', '1,3', 'examples/dummy.csv.gz']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_with_bzip2(self):
        args = ['-c', '1,3', 'examples/dummy.csv.bz2']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['a', 'c'])
        self.assertEqual(next(reader), ['1', '3'])

    def test_exclude(self):
        args = ['-C', '1,3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['b'])
        self.assertEqual(next(reader), ['2'])

    def test_include_and_exclude(self):
        args = ['-c', '1,3', '-C', '3', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['a'])
        self.assertEqual(next(reader), ['1'])

    def test_no_header_row(self):
        args = ['-c', '2', '--no-header-row', 'examples/no_header_row.csv']
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        self.assertEqual(next(reader), ['B'])
        self.assertEqual(next(reader), ['2'])
