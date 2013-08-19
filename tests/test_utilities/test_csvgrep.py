#!/usr/bin/env python

import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvgrep import CSVGrep
from csvkit.exceptions import ColumnIdentifierError, RequiredHeaderError

class TestCSVGrep(unittest.TestCase):
    def test_match(self):
        args = ['-c', '1', '-m', '1', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])

    def test_no_match(self):
        args = ['-c', '1', '-m', 'NO MATCH', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'b', 'c'])

    def test_invert_match(self):
        args = ['-c', '1', '-i', '-m', 'NO MATCH', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])

    def test_re_match(self):
        args = ['-c', '3', '-r', '^(3|9)$', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])

    def test_string_match(self):
        args = ['-c', '1', '-m', 'ILLINOIS', 'examples/realdata/FY09_EDU_Recipients_by_State.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ['State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty', 'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance', 'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program', 'TOTAL', ''])
        self.assertEqual(reader.next(), ['ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''])

    def test_invalid_column(self):
        args = ['-c', '0', '-m', '1', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = CSVGrep(args, output_file)

        self.assertRaises(ColumnIdentifierError, utility.main)
