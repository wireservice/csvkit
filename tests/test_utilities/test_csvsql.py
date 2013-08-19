#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit.utilities.csvsql import CSVSQL
from tests.utils import stderr_as_stdout

class TestCSVSQL(unittest.TestCase):
    def test_create_table(self):
        args = ['--table', 'foo', 'examples/testfixed_converted.csv']
        output_file = StringIO()

        utility = CSVSQL(args, output_file)
        utility.main() 

        sql = output_file.getvalue()

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('text VARCHAR(17) NOT NULL' in sql)
        self.assertTrue('date DATE' in sql)
        self.assertTrue('integer INTEGER' in sql)
        self.assertTrue('boolean BOOLEAN' in sql)
        self.assertTrue('float FLOAT' in sql)
        self.assertTrue('time TIME' in sql)
        self.assertTrue('datetime DATETIME' in sql)

    def test_table_argument(self):
        args = ['--table', 'foo', 'file1.csv', 'file2.csv']
        output_file = StringIO()

        utility = CSVSQL(args, output_file)

        with stderr_as_stdout(): 
            self.assertRaises(SystemExit, utility.main)

    def test_no_inference(self):
        args = ['--table', 'foo', '--no-inference', 'examples/testfixed_converted.csv']
        output_file = StringIO()

        utility = CSVSQL(args, output_file)
        utility.main() 

        sql =  output_file.getvalue()

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('text VARCHAR(17) NOT NULL' in sql)
        self.assertTrue('date VARCHAR(10) NOT NULL' in sql)
        self.assertTrue('integer VARCHAR(3) NOT NULL' in sql)
        self.assertTrue('boolean VARCHAR(5) NOT NULL' in sql)
        self.assertTrue('float VARCHAR(11) NOT NULL' in sql)
        self.assertTrue('time VARCHAR(8) NOT NULL' in sql)
        self.assertTrue('datetime VARCHAR(19) NOT NULL' in sql)

    def test_no_header_row(self):
        args = ['--table', 'foo', '--no-header-row', 'examples/no_header_row.csv']
        output_file = StringIO()

        utility = CSVSQL(args, output_file)
        utility.main() 

        sql = output_file.getvalue()

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('column1 INTEGER NOT NULL' in sql)
        self.assertTrue('column2 INTEGER NOT NULL' in sql)
        self.assertTrue('column3 INTEGER NOT NULL' in sql)

