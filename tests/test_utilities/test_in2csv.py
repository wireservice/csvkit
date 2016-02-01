#!/usr/bin/env python

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.in2csv import In2CSV, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestIn2CSV(CSVKitTestCase, EmptyFileTests):
    Utility = In2CSV
    default_args = ['-f', 'csv']

    def assertConverted(self, input_format, input_filename, output_filename, additional_args=[]):
        output = self.get_output(['-f', input_format, input_filename] + additional_args)
        self.assertEqual(output, open(output_filename, 'r').read())

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
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
        self.assertLines(['--no-header-row', 'examples/no_header_row.csv'], [
            'A,B,C',
            'True,2,3',
        ])
