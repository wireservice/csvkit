#!/usr/bin/env python

import os
import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvclean import CSVClean, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVClean(CSVKitTestCase, EmptyFileTests):
    Utility = CSVClean

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/bad.csv']):
            launch_new_instance()

    def test_simple(self):
        args = ['examples/bad.csv']
        output_file = six.StringIO()

        utility = CSVClean(args, output_file)
        utility.run()

        output_file.close()

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
        output = self.get_output_as_io(['-n', 'examples/bad.csv'])
        self.assertFalse(os.path.exists('examples/bad_err.csv'))
        self.assertFalse(os.path.exists('examples/bad_out.csv'))
        self.assertEqual(next(output)[:6], 'Line 1')
        self.assertEqual(next(output)[:6], 'Line 2')
