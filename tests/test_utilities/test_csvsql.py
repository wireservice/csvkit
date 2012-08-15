#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit.utilities.csvsql import CSVSQL
from tests.utils import stderr_as_stdout

class TestCSVSQL(unittest.TestCase):
    def test_table_argument(self):
        args = ['--table', 'foo', 'file1.csv', 'file2.csv']
        output_file = StringIO()

        utility = CSVSQL(args, output_file)

        with stderr_as_stdout(): 
            self.assertRaises(SystemExit, utility.main)

