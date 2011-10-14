#!/usr/bin/env python

import unittest
import StringIO

from csvkit.utilities.in2csv import In2CSV
from csvkit.utilities.csvstat import CSVStat

class TestIn2CSV(unittest.TestCase):
    def test_convert_xls(self):
        args = ['-f', 'xls', 'examples/test.xls']
        output_file = StringIO.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testxls_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)
