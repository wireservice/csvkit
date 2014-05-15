#!/usr/bin/env python

import StringIO
import unittest

from csvkit.utilities.csvlook import CSVLook

class TestCSVLook(unittest.TestCase):
    def test_simple(self):
        args = ['examples/dummy3.csv']
        output_file = StringIO.StringIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())

        self.assertEqual(input_file.next(), '|----+---+----|\n')
        self.assertEqual(input_file.next(), '|  a | b | c  |\n')
        self.assertEqual(input_file.next(), '|----+---+----|\n')
        self.assertEqual(input_file.next(), '|  1 | 2 | 3  |\n')
        self.assertEqual(input_file.next(), '|  1 | 4 | 5  |\n')
        self.assertEqual(input_file.next(), '|----+---+----|\n')

    def test_no_header(self):
        args = ['--no-header-row', 'examples/no_header_row3.csv']
        output_file = StringIO.StringIO()
        utility = CSVLook(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())

        #self.assertEqual(input_file.next(), '|----+---+----|\n')
        #self.assertEqual(input_file.next(), '|  1 | 2 | 3  |\n')
        #self.assertEqual(input_file.next(), '|  4 | 5 | 6  |\n')
        #self.assertEqual(input_file.next(), '|----+---+----|\n')

        self.assertEqual(input_file.next(), '|----------+---------+----------|\n')
        self.assertEqual(input_file.next(), '|  column1 | column2 | column3  |\n')
        self.assertEqual(input_file.next(), '|----------+---------+----------|\n')
        self.assertEqual(input_file.next(), '|  1       | 2       | 3        |\n')
        self.assertEqual(input_file.next(), '|  4       | 5       | 6        |\n')
        self.assertEqual(input_file.next(), '|----------+---------+----------|\n')

