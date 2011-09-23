#!/usr/bin/env python

import unittest
import StringIO

from csvkit.utilities.in2csv import In2CSV
from csvkit.utilities.csvstat import CSVStat

class TestIn2CSV(unittest.TestCase):
    def test_bad_format(self):
        args = ['-f', 'foo', 'examples/dummy.csv']
        output_file = StringIO.StringIO()
        utility = In2CSV(args, output_file)

        self.assertRaises(In2CSV.argparser.error, utility.main())
        
    def test_convert_xls(self):
        args = ['-f', 'xls', 'examples/test.xls']
        output_file = StringIO.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        # Add long string here with what the XLS file SHOULD look like,
        # then compare output_file.getvalue() with the string. Refer to
        # examples/testxls_converted.csv.
        target_output = " "
                
        self.assertEqual(output_file.getvalue(), target_output)
    
    def test_stdin_json(self):
        """
        Test whether JSON input into <stdin> converts properly. How can I
        submit data to <stdin> automatically? stdin.write.out()?
        """
    
    # Other potential tests:
    # 1. Check file formats for proper conversion -- fixed, xls, json.
    # 2. Check stdin input for error (when no file given).
    # 3. Look into schema, key, snifflimit options.
    
 

