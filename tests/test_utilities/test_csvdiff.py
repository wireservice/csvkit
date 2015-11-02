#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvdiff import CSVDiff

class TestCSVJoin(unittest.TestCase):
    def test_basic(self):
        args = ['examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVDiff(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 6)
