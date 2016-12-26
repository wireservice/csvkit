#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvsort import CSVSort, launch_new_instance
from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests, stdin_as_string


class TestCSVSort(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVSort

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        self.get_output(['examples/test_utf8.csv'])

    def test_encoding(self):
        self.get_output(['-e', 'latin1', 'examples/test_latin1.csv'])

    def test_sort_string_reverse(self):
        reader = self.get_output_as_reader(['-c', '1', '-r', 'examples/testxls_converted.csv'])
        test_order = [u'text', u'Unicode! Σ', u'This row has blanks', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader']
        new_order = [six.text_type(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_sort_date(self):
        reader = self.get_output_as_reader(['-c', '2', 'examples/testxls_converted.csv'])
        test_order = [u'text', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader', u'This row has blanks', u'Unicode! Σ']
        new_order = [six.text_type(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_no_header_row(self):
        reader = self.get_output_as_reader(['--no-header-row', '-c', '1', '-r', 'examples/no_header_row3.csv'])
        test_order = ['a', '4', '1']
        new_order = [six.text_type(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_no_inference(self):
        reader = self.get_output_as_reader(['--no-inference', '-c', '1', 'examples/test_literal_order.csv'])
        test_order = [u'a', u'192', u'27', u'3']
        new_order = [six.text_type(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_sort_t_and_nulls(self):
        reader = self.get_output_as_reader(['-c', '2', 'examples/sort_ints_nulls.csv'])
        test_order = ['b', '1', '2', '']
        new_order = [six.text_type(r[1]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_stdin(self):
        input_file = six.StringIO('a,b,c\n4,5,6\n1,2,3\n')

        with stdin_as_string(input_file):
            self.assertLines([], [
                'a,b,c',
                '1,2,3',
                '4,5,6',
            ])

        input_file.close()
