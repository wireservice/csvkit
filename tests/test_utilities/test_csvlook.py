#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvlook import CSVLook

class TestCSVLook(unittest.TestCase):
    def test_simple(self):
        args = ['examples/dummy3.csv']
        output_file = six.BytesIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.BytesIO(output_file.getvalue())

        self.assertEqual(next(input_file), b'|----+---+----|\n')
        self.assertEqual(next(input_file), b'|  a | b | c  |\n')
        self.assertEqual(next(input_file), b'|----+---+----|\n')
        self.assertEqual(next(input_file), b'|  1 | 2 | 3  |\n')
        self.assertEqual(next(input_file), b'|  1 | 4 | 5  |\n')
        self.assertEqual(next(input_file), b'|----+---+----|\n')

    def test_no_header(self):
        args = ['--no-header-row', 'examples/no_header_row3.csv']
        output_file = six.BytesIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.BytesIO(output_file.getvalue())

        self.assertEqual(next(input_file), b'|----------+---------+----------|\n')
        self.assertEqual(next(input_file), b'|  column1 | column2 | column3  |\n')
        self.assertEqual(next(input_file), b'|----------+---------+----------|\n')
        self.assertEqual(next(input_file), b'|  1       | 2       | 3        |\n')
        self.assertEqual(next(input_file), b'|  4       | 5       | 6        |\n')
        self.assertEqual(next(input_file), b'|----------+---------+----------|\n')

    def test_unicode(self):
        args = ['examples/test_utf8.csv']

        output_file = six.BytesIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = six.BytesIO(output_file.getvalue())

        self.assertEqual(next(input_file), b'|----+---+----|\n')
        self.assertEqual(next(input_file), b'|  a | b | c  |\n')
        self.assertEqual(next(input_file), b'|----+---+----|\n')
        self.assertEqual(next(input_file), b'|  1 | 2 | 3  |\n')
        self.assertEqual(next(input_file), b'|  4 | 5 | \xca\xa4  |\n')
        self.assertEqual(next(input_file), b'|----+---+----|\n')

