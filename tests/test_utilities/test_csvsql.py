#!/usr/bin/env python

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvsql import CSVSQL, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVSQL(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSQL

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_create_table(self):
        sql = self.get_output(['--table', 'foo', 'examples/testfixed_converted.csv'])

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('text VARCHAR(17) NOT NULL' in sql)
        self.assertTrue('date DATE' in sql)
        self.assertTrue('integer INTEGER' in sql)
        self.assertTrue('boolean BOOLEAN' in sql)
        self.assertTrue('float FLOAT' in sql)
        self.assertTrue('time TIME' in sql)
        self.assertTrue('datetime DATETIME' in sql)

    def test_no_inference(self):
        sql = self.get_output(['--table', 'foo', '--no-inference', 'examples/testfixed_converted.csv'])

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('text VARCHAR(17) NOT NULL' in sql)
        self.assertTrue('date VARCHAR(10) NOT NULL' in sql)
        self.assertTrue('integer VARCHAR(3) NOT NULL' in sql)
        self.assertTrue('boolean VARCHAR(5) NOT NULL' in sql)
        self.assertTrue('float VARCHAR(11) NOT NULL' in sql)
        self.assertTrue('time VARCHAR(8) NOT NULL' in sql)
        self.assertTrue('datetime VARCHAR(19) NOT NULL' in sql)

    def test_no_header_row(self):
        sql = self.get_output(['--table', 'foo', '--no-header-row', 'examples/no_header_row.csv'])

        self.assertTrue('CREATE TABLE foo' in sql)
        self.assertTrue('a INTEGER NOT NULL' in sql)
        self.assertTrue('b INTEGER NOT NULL' in sql)
        self.assertTrue('c INTEGER NOT NULL' in sql)

    def test_stdin(self):
        input_file = six.StringIO('a,b,c\n1,2,3\n')

        with stdin_as_string(input_file):
            sql = self.get_output(['--table', 'foo'])

            self.assertTrue('CREATE TABLE foo' in sql)
            self.assertTrue('a INTEGER NOT NULL' in sql)
            self.assertTrue('b INTEGER NOT NULL' in sql)
            self.assertTrue('c INTEGER NOT NULL' in sql)

    def test_stdin_and_filename(self):
        input_file = six.StringIO("a,b,c\n1,2,3\n")

        with stdin_as_string(input_file):
            sql = self.get_output(['examples/dummy.csv'])

            self.assertTrue('CREATE TABLE stdin' in sql)
            self.assertTrue('CREATE TABLE dummy' in sql)

    def test_empty_with_query(self):
        with stdin_as_string(six.StringIO()):
            utility = CSVSQL(['--query', 'select 1'], six.StringIO())
            utility.main()

    def test_query(self):
        input_file = six.StringIO("a,b,c\n1,2,3\n")

        with stdin_as_string(input_file):
            sql = self.get_output(['--query', 'select m.usda_id, avg(i.sepal_length) as mean_sepal_length from iris as i join irismeta as m on (i.species = m.species) group by m.species', 'examples/iris.csv', 'examples/irismeta.csv'])

            if six.PY2:
                self.assertTrue('usda_id,mean_sepal_length' in sql)
                self.assertTrue('IRSE,5.006' in sql)
                self.assertTrue('IRVE2,5.936' in sql)
                self.assertTrue('IRVI,6.588' in sql)
            else:
                self.assertTrue('usda_id,mean_sepal_length' in sql)
                self.assertTrue('IRSE,5.005' in sql)
                self.assertTrue('IRVE2,5.936' in sql)
                self.assertTrue('IRVI,6.587' in sql)
