#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit.utilities.csvfuzzyjoin import CSVFuzzyJoin

class TestCSVFuzzyJoin(unittest.TestCase):

    def test(self):
        args = ['examples/fuzzy_main.csv', 'examples/fuzzy_lookup.csv','-f','name=office']
        output_file = StringIO()

        utility = CSVFuzzyJoin(args, output_file)
        utility.main()

        output = output_file.getvalue()
        saved_results = open('examples/fuzzy_results.csv','r').read()

        self.assertEqual(output,saved_results)

    def test_with_hard(self):
        args = ['examples/fuzzy_main.csv', 'examples/fuzzy_lookup.csv','-f','name=office','-n','state,party']
        output_file = StringIO()

        utility = CSVFuzzyJoin(args, output_file)
        utility.main()

        output = output_file.getvalue()
        saved_results = open('examples/fuzzy_hard_results.csv','r').read()

        self.assertEqual(output,saved_results)


