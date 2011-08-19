#!/usr/bin/env python

import StringIO
import unittest

from csvkit.exceptions import NonUniqueKeyColumnException
from csvkit.utilities.csvjson import CSVJSON

class TestCSVStack(unittest.TestCase):
    def test_simple(self):
        args = ['examples/dummy.csv']
        output_file = StringIO.StringIO()

        utility = CSVJSON(args, output_file)
        utility.main()

        self.assertEqual(output_file.getvalue(), '[{"a": "1", "c": "3", "b": "2"}]')

    def test_indentation(self):
        args = ['-i', '4', 'examples/dummy.csv']
        output_file = StringIO.StringIO()

        utility = CSVJSON(args, output_file)
        utility.main()

        self.assertEqual(output_file.getvalue(), '[\n    {\n        "a": "1", \n        "c": "3", \n        "b": "2"\n    }\n]')

    def test_keying(self):
        args = ['-k', 'a', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()

        self.assertEqual(output_file.getvalue(), '{"1": {"a": "1", "c": "3", "b": "2"}}')

    def test_duplicate_keys(self):
        args = ['-k', 'a', 'examples/dummy3.csv']
        output_file = StringIO.StringIO()
        
        utility = CSVJSON(args, output_file)

        self.assertRaises(NonUniqueKeyColumnException, utility.main)
