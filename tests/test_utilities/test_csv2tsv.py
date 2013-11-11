#!/usr/bin/env python

import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csv2tsv import CSV2TSV

class TestCSV2TSV(unittest.TestCase):

    def test_tsv(self):
        args = ['examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSV2TSV(args, output_file)
        utility.main()
        input_file = StringIO.StringIO(output_file.getvalue())
        self.assertEqual(input_file.next(), 'a\tb\tc\n')
        self.assertEqual(input_file.next(), '1\t2\t3\n')

    def test_delimiter(self):
        args = ['-D', '|', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSV2TSV(args, output_file)
        utility.main()
        input_file = StringIO.StringIO(output_file.getvalue())
        self.assertEqual(input_file.next(), 'a|b|c\n')
        self.assertEqual(input_file.next(), '1|2|3\n')

    def test_quoting(self):
        args = ['-U', '1', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSV2TSV(args, output_file)
        utility.main()
        input_file = StringIO.StringIO(output_file.getvalue())
        self.assertEqual(input_file.next(), '"a"\t"b"\t"c"\n')
        self.assertEqual(input_file.next(), '"1"\t"2"\t"3"\n')

    def test_quotechar(self):
        args = ['-Q', "'", '-U', '1', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSV2TSV(args, output_file)
        utility.main()
        input_file = StringIO.StringIO(output_file.getvalue())
        self.assertEqual(input_file.next(), "'a'\t'b'\t'c'\n")
        self.assertEqual(input_file.next(), "'1'\t'2'\t'3'\n")
