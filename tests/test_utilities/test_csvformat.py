#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvformat import CSVFormat
from tests.utils import stdin_as_string

class TestCSVFormat(unittest.TestCase):
    def test_delimiter(self):
        args = ['-D', '|', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVFormat(args, output_file)
        utility.main()

        lines = output_file.getvalue().split('\n')

        self.assertEqual(lines[0], 'a|b|c')
        self.assertEqual(lines[1], '1|2|3')

    def test_tab_delimiter(self):
        args = ['-T', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVFormat(args, output_file)
        utility.main()

        lines = output_file.getvalue().split('\n')

        self.assertEqual(lines[0], 'a\tb\tc')
        self.assertEqual(lines[1], '1\t2\t3')

    def test_quoting(self):
        args = ['-Q', '*', '-U', '0', '-B']
        output_file = six.StringIO()

        input_file = six.StringIO('a,b,c\n1*2,3,4\n')

        with stdin_as_string(input_file):
            utility = CSVFormat(args, output_file)
            utility.main()

            lines = output_file.getvalue().split('\n')

            self.assertEqual(lines[0], 'a,b,c')
            self.assertEqual(lines[1], '*1**2*,3,4')

    def test_escapechar(self):
        args = ['-P', '#', '-U', '3']
        output_file = six.StringIO()
    
        input_file = six.StringIO('a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            utility = CSVFormat(args, output_file)
            utility.main()

            lines = output_file.getvalue().split('\n')

            self.assertEqual(lines[0], 'a,b,c')
            self.assertEqual(lines[1], '1#"2,3,4')

    def test_lineterminator(self):
        args = ['-M', 'XYZ', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVFormat(args, output_file)
        utility.main()

        output = output_file.getvalue()

        self.assertEqual(output, 'a,b,cXYZ1,2,3XYZ')

