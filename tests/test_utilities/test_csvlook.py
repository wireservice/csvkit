#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    import unittest2 as unittest
    from mock import patch
except ImportError:
    import unittest
    from unittest.mock import patch

from csvkit.utilities.csvlook import CSVLook, launch_new_instance


class TestCSVLook(unittest.TestCase):

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvlook', 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        args = ['examples/dummy3.csv']
        output_file = six.StringIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())

        self.assertEqual(next(input_file), '|----+---+----|\n')
        self.assertEqual(next(input_file), '|  a | b | c  |\n')
        self.assertEqual(next(input_file), '|----+---+----|\n')
        self.assertEqual(next(input_file), '|  1 | 2 | 3  |\n')
        self.assertEqual(next(input_file), '|  1 | 4 | 5  |\n')
        self.assertEqual(next(input_file), '|----+---+----|\n')

    def test_no_header(self):
        args = ['--no-header-row', 'examples/no_header_row3.csv']
        output_file = six.StringIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())

        self.assertEqual(next(input_file), '|----------+---------+----------|\n')
        self.assertEqual(next(input_file), '|  column1 | column2 | column3  |\n')
        self.assertEqual(next(input_file), '|----------+---------+----------|\n')
        self.assertEqual(next(input_file), '|  1       | 2       | 3        |\n')
        self.assertEqual(next(input_file), '|  4       | 5       | 6        |\n')
        self.assertEqual(next(input_file), '|----------+---------+----------|\n')

    def test_unicode(self):
        args = ['examples/test_utf8.csv']

        output_file = six.StringIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())

        self.assertEqual(next(input_file), '|----+---+----|\n')
        self.assertEqual(next(input_file), '|  a | b | c  |\n')
        self.assertEqual(next(input_file), '|----+---+----|\n')
        self.assertEqual(next(input_file), '|  1 | 2 | 3  |\n')
        self.assertEqual(next(input_file), u'|  4 | 5 | ʤ  |\n')
        self.assertEqual(next(input_file), '|----+---+----|\n')
