#!/usr/bin/env python

import os

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.utilities.csvclean import CSVClean

class TestCSVClean(unittest.TestCase):
    def test_simple(self):
        args = ['examples/bad.csv']
        output_file = six.StringIO()

        utility = CSVClean(args, output_file)
        utility.main()

        self.assertTrue(os.path.exists('examples/bad_err.csv'))
        self.assertTrue(os.path.exists('examples/bad_out.csv'))

        try:
            with open('examples/bad_err.csv') as f:
                next(f)
                self.assertEqual(next(f)[0], '1')
                self.assertEqual(next(f)[0], '2')
                self.assertRaises(StopIteration, next, f)
                
            with open('examples/bad_out.csv') as f:
                next(f)
                self.assertEqual(next(f)[0], '0')
                self.assertRaises(StopIteration, next, f)
        finally:
            # Cleanup
            os.remove('examples/bad_err.csv')
            os.remove('examples/bad_out.csv')

    def test_dry_run(self):
        args = ['-n', 'examples/bad.csv']
        output_file = six.StringIO()

        utility = CSVClean(args, output_file)
        utility.main()

        self.assertFalse(os.path.exists('examples/bad_err.csv'))
        self.assertFalse(os.path.exists('examples/bad_out.csv'))

        output = six.StringIO(output_file.getvalue())

        self.assertEqual(next(output)[:6], 'Line 1')
        self.assertEqual(next(output)[:6], 'Line 2')

