#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvcut import CSVCut, launch_new_instance
from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests


class TestCSVCut(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVCut

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
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
            ['b'],
            ['2'],
        ])
