#!/usr/bin/env python

import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvcut import CSVCut

class TestCSVCut(unittest.TestCase):
    def test_simple(self):
        args = ['-c', '1,3', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'c'])
        self.assertEqual(reader.next(), ['1', '3'])

    def test_names(self):
        args = ['-n', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())

        self.assertEqual(input_file.next(), '  1: a\n')
        self.assertEqual(input_file.next(), '  2: b\n')
        self.assertEqual(input_file.next(), '  3: c\n')

    def test_with_gzip(self):
        args = ['-c', '1,3', 'examples/dummy.csv.gz']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'c'])
        self.assertEqual(reader.next(), ['1', '3'])

    def test_with_bzip2(self):
        args = ['-c', '1,3', 'examples/dummy.csv.bz2']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'c'])
        self.assertEqual(reader.next(), ['1', '3'])

    def test_exclude(self):
        args = ['-C', '1,3', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['b'])
        self.assertEqual(reader.next(), ['2'])

    def test_include_and_exclude(self):
        args = ['-c', '1,3', '-C', '3', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVCut(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a'])
        self.assertEqual(reader.next(), ['1'])

