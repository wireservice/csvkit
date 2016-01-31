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
from tests.utils import ColumnsTests, NamesTests


class TestCSVCut(unittest.TestCase, ColumnsTests, NamesTests):
    Utility = CSVCut

    def assertRows(self, args, rows):
        output_file = six.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        for row in rows:
            self.assertEqual(next(reader), row)

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvcut', 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        self.assertRows(['-c', '1,3', 'examples/dummy.csv'], [
            ['a', 'c'],
            ['1', '3'],
        ])

    def test_unicode(self):
        self.assertRows(['-c', '1,3', 'examples/test_utf8.csv'], [
            ['foo', 'baz'],
            ['1', '3'],
            ['4', u'ʤ'],
        ])

    def test_with_gzip(self):
        self.assertRows(['-c', '1,3', 'examples/dummy.csv.gz'], [
            ['a', 'c'],
            ['1', '3'],
        ])

    def test_with_bzip2(self):
        self.assertRows(['-c', '1,3', 'examples/dummy.csv.bz2'], [
            ['a', 'c'],
            ['1', '3'],
        ])

    def test_exclude(self):
        self.assertRows(['-C', '1,3', 'examples/dummy.csv'], [
            ['b'],
            ['2'],
        ])

    def test_include_and_exclude(self):
        self.assertRows(['-c', '1,3', '-C', '3', 'examples/dummy.csv'], [
            ['a'],
            ['1'],
        ])

    def test_no_header_row(self):
        self.assertRows(['-c', '2', '--no-header-row', 'examples/no_header_row.csv'], [
            ['B'],
            ['2'],
        ])
