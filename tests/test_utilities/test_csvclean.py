#!/usr/bin/env python

from cStringIO import StringIO
import os
import unittest

from csvkit.utilities.csvclean import CSVClean

class TestCSVClean(unittest.TestCase):
    def test_simple(self):
        args = ['examples/bad.csv']
        output_file = StringIO()

        utility = CSVClean(args, output_file)
        utility.main()

        self.assertTrue(os.path.exists('examples/bad_err.csv'))
        self.assertTrue(os.path.exists('examples/bad_out.csv'))

        try:
            with open('examples/bad_err.csv') as f:
                f.next()
                self.assertEqual(f.next()[0], '1')
                self.assertEqual(f.next()[0], '2')
                self.assertRaises(StopIteration, f.next)
                
            with open('examples/bad_out.csv') as f:
                f.next()
                self.assertEqual(f.next()[0], '0')
                self.assertRaises(StopIteration, f.next)
        finally:
            # Cleanup
            os.remove('examples/bad_err.csv')
            os.remove('examples/bad_out.csv')

    def test_dry_run(self):
        args = ['-n', 'examples/bad.csv']
        output_file = StringIO()

        utility = CSVClean(args, output_file)
        utility.main()

        self.assertFalse(os.path.exists('examples/bad_err.csv'))
        self.assertFalse(os.path.exists('examples/bad_out.csv'))

        output = StringIO(output_file.getvalue())

        self.assertEqual(output.next()[:6], 'Line 1')
        self.assertEqual(output.next()[:6], 'Line 2')

