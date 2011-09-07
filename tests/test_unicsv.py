#!/usr/bin/env python

import unittest
import csv
import os

from csvkit import unicsv

class TestUnicodeClasses(unittest.TestCase):
    def setUp(self):
        self.lim = csv.field_size_limit()
        with open('dummy.csv', 'w') as f:
            f.write('a' * 10)
            f.close()

    def test_maxfieldsize(self):
        # Testing --maxfieldsize for failure. Creating data using str * int.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=9)
            with self.assertRaises(unicsv.FieldSizeLimitError):
                c.next()

        # Now testing higher --maxfieldsize.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=11)
            self.assertEqual(['a' * 10], c.next())

    def tearDown(self):
        # Resetting limit to avoid failure in other tests.
        csv.field_size_limit(self.lim)
        self.lim = None
        os.system('rm dummy.csv')
