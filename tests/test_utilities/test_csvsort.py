#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import agate
import six

try:
    import unittest2 as unittest
    from mock import patch
except ImportError:
    import unittest
    from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError, RequiredHeaderError
from csvkit.utilities.csvsort import CSVSort, launch_new_instance


class TestCSVSort(unittest.TestCase):

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvsort', 'examples/dummy.csv']):
            launch_new_instance()

    def test_sort_string_reverse(self):
        args = ['-c', '1', '-r', 'examples/testxls_converted.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        test_order = [u'text', u'Unicode! Σ', u'This row has blanks', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader']
        new_order = [six.text_type(r[0]) for r in reader]

        self.assertEqual(test_order, new_order)

    def test_sort_date(self):
        args = ['-c', '2', 'examples/testxls_converted.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        test_order = [u'text', u'This row has blanks', u'Unicode! Σ', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader']
        new_order = [six.text_type(r[0]) for r in reader]

        self.assertEqual(test_order, new_order)

    def test_invalid_column(self):
        args = ['-c', '0', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        self.assertRaises(ColumnIdentifierError, utility.main)

    def test_invalid_options(self):
        args = ['-n', '--no-header-row', 'examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        self.assertRaises(RequiredHeaderError, utility.main)

    def test_no_header_row(self):
        args = ['--no-header-row', '-c', '1', '-r', 'examples/no_header_row3.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        test_order = ['A', '4', '1']
        new_order = [six.text_type(r[0]) for r in reader]

        self.assertEqual(test_order, new_order)

    def test_no_inference(self):
        args = ['--no-inference', '-c', '1', 'examples/test_literal_order.csv']
        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        test_order = [u'a', u'192', u'27', u'3']
        new_order = [six.text_type(r[0]) for r in reader]

        self.assertEqual(test_order, new_order)

    def test_sort_ints_and_nulls(self):
        args = ['-c', '2', 'examples/sort_ints_nulls.csv']

        output_file = six.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = six.StringIO(output_file.getvalue())
        reader = agate.reader(input_file)

        test_order = ['b', '', '1', '2']
        new_order = [six.text_type(r[1]) for r in reader]

        self.assertEqual(test_order, new_order)
