#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit.utilities.csvjoin import CSVJoin

class TestCSVJoin(unittest.TestCase):
    def test_sequential(self):
        args = ['examples/join_a.csv', 'examples/join_b.csv']
        output_file = StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 4)

    def test_inner(self):
        args = ['-c', 'a', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 3)

    def test_left(self):
        args = ['-c', 'a', '--left', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 5)

    def test_right(self):
        args = ['-c', 'a', '--right', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 4)

    def test_outer(self):
        args = ['-c', 'a', '--outer', 'examples/join_a.csv', 'examples/join_b.csv']
        output_file = StringIO()

        utility = CSVJoin(args, output_file)
        utility.main()

        output = StringIO(output_file.getvalue())

        self.assertEqual(len(output.readlines()), 6)

