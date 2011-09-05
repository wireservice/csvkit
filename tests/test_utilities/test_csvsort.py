#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvsort import CSVSort

class TestCSVSort(unittest.TestCase):
    def test_sort_string_reverse(self):
        args = ['-c', '1', '-r', 'examples/testxls_converted.csv']
        output_file = StringIO.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        test_order = [u'text', u'Unicode! Σ', u'This row has blanks', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader']
        new_order = [unicode(r[0]) for r in reader] 

        self.assertEqual(test_order, new_order)

    def test_sort_date(self):
        args = ['-c', '2', 'examples/testxls_converted.csv']
        output_file = StringIO.StringIO()
        utility = CSVSort(args, output_file)

        utility.main()

        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        test_order = [u'text', u'This row has blanks', u'Unicode! Σ', u'Chicago Tribune', u'Chicago Sun-Times', u'Chicago Reader']
        new_order = [unicode(r[0]) for r in reader] 

        self.assertEqual(test_order, new_order)

