#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvlook import CSVLook, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVLook(CSVKitTestCase, EmptyFileTests):
    Utility = CSVLook

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        self.assertLines(['examples/dummy3.csv'], [
            '|-------+---+----|',
            '|     a | b | c  |',
            '|-------+---+----|',
            '|  True | 2 | 3  |',
            '|  True | 4 | 5  |',
            '|-------+---+----|',
        ])

    def test_no_header(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row3.csv'], [
            '|----+---+----|',
            '|  a | b | c  |',
            '|----+---+----|',
            '|  1 | 2 | 3  |',
            '|  4 | 5 | 6  |',
            '|----+---+----|',
        ])

    def test_unicode(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '|------+-----+------|',
            '|  foo | bar | baz  |',
            '|------+-----+------|',
            '|    1 |   2 | 3    |',
            u'|    4 |   5 | ʤ    |',
            '|------+-----+------|',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy3.csv'], [
            '|---------------+------+---+----|',
            '|  line_numbers |    a | b | c  |',
            '|---------------+------+---+----|',
            '|             1 | True | 2 | 3  |',
            '|             2 | True | 4 | 5  |',
            '|---------------+------+---+----|',
        ])
