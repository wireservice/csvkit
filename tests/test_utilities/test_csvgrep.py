#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvgrep import CSVGrep
from csvkit.exceptions import ColumnIdentifierError

class TestCSVGrep(unittest.TestCase):
    def test_match(self):
        args = ['-c', '1', '-m', '1', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])

    def test_no_match(self):
        args = ['-c', '1', '-m', 'NO MATCH', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'b', 'c'])

    def test_invert_match(self):
        args = ['-c', '1', '-i', '-m', 'NO MATCH', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])

    def test_re_match(self):
        args = ['-c', '3', '-r', '^(3|9)$', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])

    def test_string_match(self):
        args = ['-c', '1', '-m', 'ILLINOIS', 'examples/realdata/FY09_EDU_Recipients_by_State.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(next(reader), ['State Name', 'State Abbreviate', 'Code', 'Montgomery GI Bill-Active Duty', 'Montgomery GI Bill- Selective Reserve', 'Dependents\' Educational Assistance', 'Reserve Educational Assistance Program', 'Post-Vietnam Era Veteran\'s Educational Assistance Program', 'TOTAL', ''])
        self.assertEqual(next(reader), ['ILLINOIS', 'IL', '17', '15,659', '2,491', '2,025', '1,770', '19', '21,964', ''])

    def test_invalid_column(self):
        args = ['-c', '0', '-m', '1', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGrep(args, output_file)

        self.assertRaises(ColumnIdentifierError, utility.main)
