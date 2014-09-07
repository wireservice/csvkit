#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvjoin import CSVJoin

class TestCSVJoin(unittest.TestCase):
    def test_sequential(self):
        args = ['examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 4)

    def test_inner(self):
        args = ['-c', 'a', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 3)

    def test_left(self):
        args = ['-c', 'a', '--left', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 5)

    def test_right(self):
        args = ['-c', 'a', '--right', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 4)

    def test_outer(self):
        args = ['-c', 'a', '--outer', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 6)

    def test_left_short_columns(self):
        args = ['-c', 'a', 'examples/join_a_short.csv', 'examples/join_b.csv']
        output_file = six.StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = six.StringIO(output_file.getvalue())

        with open('examples/join_short.csv') as f:
            self.assertEqual(output.readlines(), f.readlines())

