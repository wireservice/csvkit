#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import six
from sqlalchemy.exc import IntegrityError, OperationalError

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvsql import CSVSQL, launch_new_instance
from csvkit.utilities.sql2csv import SQL2CSV
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVSQL(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSQL

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def setUp(self):
        self.db_file = 'foo.db'

    def tearDown(self):
        try:
            os.remove(self.db_file)
        except OSError:
            pass

    def test_create_table(self):
        sql = self.get_output(['--tables', 'foo', 'examples/testfixed_converted.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  text VARCHAR NOT NULL, 
  date DATE, 
  integer DECIMAL, 
  boolean BOOLEAN, 
  float DECIMAL, 
  time DATETIME, 
  datetime TIMESTAMP, 
  empty_column BOOLEAN
);
''')  # noqa

    def test_no_blanks(self):
        sql = self.get_output(['--tables', 'foo', 'examples/blanks.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  a BOOLEAN, 
  b BOOLEAN, 
  c BOOLEAN, 
  d BOOLEAN, 
  e BOOLEAN, 
  f BOOLEAN
);
''')  # noqa

    def test_blanks(self):
        sql = self.get_output(['--tables', 'foo', '--blanks', 'examples/blanks.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  a VARCHAR NOT NULL, 
  b VARCHAR NOT NULL, 
  c VARCHAR NOT NULL, 
  d VARCHAR NOT NULL, 
  e VARCHAR NOT NULL, 
  f VARCHAR NOT NULL
);
''')  # noqa

    def test_no_inference(self):
        sql = self.get_output(['--tables', 'foo', '--no-inference', 'examples/testfixed_converted.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  text VARCHAR NOT NULL, 
  date VARCHAR, 
  integer VARCHAR, 
  boolean VARCHAR, 
  float VARCHAR, 
  time VARCHAR, 
  datetime VARCHAR, 
  empty_column VARCHAR
);
''')  # noqa

    def test_no_header_row(self):
        sql = self.get_output(['--tables', 'foo', '--no-header-row', 'examples/no_header_row.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  a BOOLEAN NOT NULL, 
  b DECIMAL NOT NULL, 
  c DECIMAL NOT NULL
);
''')  # noqa

    def test_linenumbers(self):
        sql = self.get_output(['--tables', 'foo', '--linenumbers', 'examples/dummy.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  a BOOLEAN NOT NULL, 
  b DECIMAL NOT NULL, 
  c DECIMAL NOT NULL
);
''')  # noqa

    def test_stdin(self):
        input_file = six.StringIO('a,b,c\n4,2,3\n')

        with stdin_as_string(input_file):
            sql = self.get_output(['--tables', 'foo'])

            self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  a DECIMAL NOT NULL, 
  b DECIMAL NOT NULL, 
  c DECIMAL NOT NULL
);
''')  # noqa

        input_file.close()

    def test_stdin_and_filename(self):
        input_file = six.StringIO("a,b,c\n1,2,3\n")

        with stdin_as_string(input_file):
            sql = self.get_output(['-', 'examples/dummy.csv'])

            self.assertTrue('CREATE TABLE stdin' in sql)
            self.assertTrue('CREATE TABLE dummy' in sql)

        input_file.close()

    def test_query(self):
        input_file = six.StringIO("a,b,c\n1,2,3\n")

        with stdin_as_string(input_file):
            sql = self.get_output(['--query', 'SELECT m.usda_id, avg(i.sepal_length) AS mean_sepal_length FROM iris '
                                   'AS i JOIN irismeta AS m ON (i.species = m.species) GROUP BY m.species',
                                   'examples/iris.csv', 'examples/irismeta.csv'])

            self.assertTrue('usda_id,mean_sepal_length' in sql)
            self.assertTrue('IRSE,5.00' in sql)
            self.assertTrue('IRVE2,5.936' in sql)
            self.assertTrue('IRVI,6.58' in sql)

        input_file.close()

    def test_query_empty(self):
        input_file = six.StringIO()

        with stdin_as_string(input_file):
            output = self.get_output(['--query', 'SELECT 1'])
            self.assertEqual(output, '1\n1\n')

        input_file.close()

    def test_query_text(self):
        sql = self.get_output(['--query', 'SELECT text FROM testfixed_converted WHERE text LIKE "Chicago%"',
                               'examples/testfixed_converted.csv'])

        self.assertEqual(sql,
            "text\n"
            "Chicago Reader\n"
            "Chicago Sun-Times\n"
            "Chicago Tribune\n")

    def test_query_file(self):
        sql = self.get_output(['--query', 'examples/test_query.sql', 'examples/testfixed_converted.csv'])

        self.assertEqual(sql,
            "question,text\n"
            "36,©\n")

    def test_before_after_insert(self):
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', 'examples/dummy.csv', '--before-insert',
                         'SELECT 1; CREATE TABLE foobar (date DATE)', '--after-insert', 'INSERT INTO dummy VALUES (0, 5, 6)'])

        output_file = six.StringIO()
        utility = SQL2CSV(['--db', 'sqlite:///' + self.db_file, '--query', 'SELECT * FROM foobar'], output_file)
        utility.run()
        output = output_file.getvalue()
        output_file.close()
        self.assertEqual(output, 'date\n')

        output_file = six.StringIO()
        utility = SQL2CSV(['--db', 'sqlite:///' + self.db_file, '--query', 'SELECT * FROM dummy'], output_file)
        utility.run()
        output = output_file.getvalue()
        output_file.close()
        self.assertEqual(output, 'a,b,c\n1,2,3\n0,5,6\n')

    def test_no_prefix_unique_constraint(self):
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', 'examples/dummy.csv', '--unique-constraint', 'a'])
        with self.assertRaises(IntegrityError):
            self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', 'examples/dummy.csv', '--no-create'])

    def test_prefix_unique_constraint(self):
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', 'examples/dummy.csv', '--unique-constraint', 'a'])
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', 'examples/dummy.csv', '--no-create', '--prefix', 'OR IGNORE'])

    def test_no_create_if_not_exists(self):
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', '--tables', 'foo', 'examples/foo1.csv'])
        with self.assertRaises(OperationalError):
            self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', '--tables', 'foo', 'examples/foo2.csv'])

    def test_create_if_not_exists(self):
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', '--tables', 'foo', 'examples/foo1.csv'])
        self.get_output(['--db', 'sqlite:///' + self.db_file, '--insert', '--tables', 'foo', 'examples/foo2.csv', '--create-if-not-exists'])
