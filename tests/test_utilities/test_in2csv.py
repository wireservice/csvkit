#!/usr/bin/env python

import unittest
import StringIO

from csvkit.utilities.in2csv import In2CSV

class TestIn2CSV(unittest.TestCase):
    def test_bad_format(self):
        args = ['-f', 'foo', 'examples/dummy.csv']
        output_file = StringIO.StringIO()

        self.assertRaises(In2CSV.argparser.error, In2CSV(args, output_file))
    
    # Other potential tests:
    # 1. Check file formats for proper conversion -- fixed, xls, json.
    # 2. Check stdin input for error (when no file given).
    # 3. Look into schema, key, snifflimit options.
    
 

