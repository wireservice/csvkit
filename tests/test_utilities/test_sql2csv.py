#!/usr/bin/env python

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os

from csvkit.utilities.sql2csv import SQL2CSV
from csvkit.utilities.csvsql import CSVSQL
from tests.utils import stdin_as_string

class TestSQL2CSV(unittest.TestCase):
    def setUp(self):
        self.db_file = "foo.db"

    def tearDown(self):
        try:
            os.remove(self.db_file)
        except OSError:
            pass

    def csvsql(self, csv_file):
        """
        Load test data into the DB and return it as a string for comparison.
        """
        args = ['--db', "sqlite:///" + self.db_file, '--table', 'foo', '--insert', csv_file]

        utility = CSVSQL(args)
        utility.main()

        return open(csv_file, 'r').read().strip()

    def test_query(self):
        args = ['--query', 'select 6*9 as question']
        output_file = six.StringIO()

        utility = SQL2CSV(args, output_file)
        utility.main()
        csv = output_file.getvalue()

        self.assertTrue('question' in csv)
        self.assertTrue('54' in csv)

    def test_stdin(self):
        output_file = six.StringIO()
        input_file = six.StringIO("select cast(3.1415 * 13.37 as integer) as answer")

        with stdin_as_string(input_file):
            utility = SQL2CSV([], output_file)
            utility.main()
            csv = output_file.getvalue()

            self.assertTrue('answer' in csv)
            self.assertTrue('42' in csv)

    def test_stdin_with_query(self):
        args = ['--query', 'select 6*9 as question']
        output_file = six.StringIO()
        input_file = six.StringIO("select cast(3.1415 * 13.37 as integer) as answer")

        with stdin_as_string(input_file):
            utility = SQL2CSV(args, output_file)
            utility.main()
            csv = output_file.getvalue()

            self.assertTrue('question' in csv)
            self.assertTrue('42' not in csv)

    def test_unicode(self):
        target_output = self.csvsql('examples/test_utf8.csv')
        args = ['--db', "sqlite:///" + self.db_file, '--query', 'select * from foo']
        output_file = six.StringIO()

        utility = SQL2CSV(args, output_file)
        utility.main()

        self.assertEqual(output_file.getvalue().strip(), target_output)

    def test_no_header_row(self):
        self.csvsql('examples/dummy.csv')
        args = ['--db', "sqlite:///" + self.db_file, '--no-header-row', '--query', 'select * from foo']
        output_file = six.StringIO()
        utility = SQL2CSV(args, output_file)
        utility.main()
        csv = output_file.getvalue()

        self.assertTrue('a,b,c' not in csv)
        self.assertTrue('1,2,3' in csv)

    def test_linenumbers(self):
        self.csvsql('examples/dummy.csv')
        args = ['--db', "sqlite:///" + self.db_file, '--linenumbers', '--query', 'select * from foo']
        output_file = six.StringIO()
        utility = SQL2CSV(args, output_file)
        utility.main()
        csv = output_file.getvalue()

        self.assertTrue('line_number,a,b,c' in csv)
        self.assertTrue('1,1,2,3' in csv)
