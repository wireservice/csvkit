#!/usr/bin/env python

import sys

import six

try:
    import unittest2 as unittest
    from mock import patch
except ImportError:
    import unittest
    from unittest.mock import patch

from csvkit.utilities.in2csv import In2CSV, launch_new_instance


class TestIn2CSV(unittest.TestCase):
    def assertConverted(self, input_format, input_filename, output_filename, additional_args=[]):
        args = ['-f', input_format, input_filename] + additional_args
        output_file = six.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        target_output = open(output_filename, 'r').read()
        self.assertEqual(output_file.getvalue(), target_output)

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['in2csv', 'examples/dummy.csv']):
            launch_new_instance()

    def test_convert_csv(self):
        self.assertConverted('csv', 'examples/testfixed_converted.csv', 'examples/testfixed_converted.csv')

    def test_convert_dbf(self):
        self.assertConverted('dbf', 'examples/testdbf.dbf', 'examples/testdbf_converted.csv')

    def test_convert_json(self):
        self.assertConverted('json', 'examples/testjson.json', 'examples/testjson_converted.csv')

    def test_convert_ndjson(self):
        self.assertConverted('ndjson', 'examples/testjson_multiline.json', 'examples/testjson_multiline_converted.csv')

    def test_convert_nested_json(self):
        self.assertConverted('json', 'examples/testjson_nested.json', 'examples/testjson_nested_converted.csv')

    def test_convert_xls(self):
        self.assertConverted('xls', 'examples/test.xls', 'examples/testxls_converted.csv')

    def test_convert_xls_with_sheet(self):
        self.assertConverted('xls', 'examples/sheets.xls', 'examples/testxls_converted.csv', ['--sheet', 'data'])

    def test_convert_xlsx(self):
        self.assertConverted('xlsx', 'examples/test.xlsx', 'examples/testxlsx_converted.csv')

    def test_convert_xlsx_with_sheet(self):
        self.assertConverted('xlsx', 'examples/sheets.xlsx', 'examples/testxlsx_converted.csv', ['--sheet', 'data'])

    def test_csv_no_headers(self):
        args = ['--no-header-row', 'examples/no_header_row.csv']
        output_file = six.StringIO()

        utility = In2CSV(args, output_file)
        utility.main()

        output = output_file.getvalue()

        self.assertTrue('A,B,C' in output)
