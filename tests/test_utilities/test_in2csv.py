#!/usr/bin/env python

import unittest
import StringIO

from csvkit.utilities.in2csv import In2CSV

class TestIn2CSV(unittest.TestCase):
    def test_convert_xls(self):
        args = ['-f', 'xls', 'examples/test.xls']
        output_file = StringIO.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testxls_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_convert_specific_xls_sheet(self):
        args = ['-f', 'xls', '--sheet', 'Sheet2', 'examples/sheets.xls']
        output_file = StringIO.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        target_output = open('examples/sheetsxls_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_csv_no_headers(self):
        args = ['--no-header-row', 'examples/no_header_row.csv']
        output_file = StringIO.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        output = output_file.getvalue()

        self.assertTrue('column1,column2,column3' in output)
