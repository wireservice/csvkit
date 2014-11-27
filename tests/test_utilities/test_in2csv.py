#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.in2csv import In2CSV

class TestIn2CSV(unittest.TestCase):
    def test_convert_xls(self):
        args = ['-f', 'xls', 'examples/test.xls']
        output_file = six.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testxls_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_convert_xlsx(self):
        args = ['-f', 'xlsx', 'examples/test.xlsx']
        output_file = six.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testxlsx_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_convert_specific_xls_sheet(self):
        args = ['-f', 'xls', '--sheet', 'Sheet2', 'examples/sheets.xls']
        output_file = six.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        target_output = open('examples/sheetsxls_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_csv_no_headers(self):
        args = ['--no-header-row', 'examples/no_header_row.csv']
        output_file = six.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        output = output_file.getvalue()

        self.assertTrue('column1,column2,column3' in output)
      
    def test_convert_json(self):
        args = ['examples/testjson.json']
        output_file = six.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testjson_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_convert_ndjson(self):
        args = ['examples/testjson_multiline.json', '-f', 'ndjson']
        output_file = six.StringIO()
        
        utility = In2CSV(args, output_file)
        utility.main()
        
        target_output = open('examples/testjson_multiline_converted.csv', 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

