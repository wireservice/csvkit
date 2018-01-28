#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import six
from sqlalchemy import Index, MetaData, Table, create_engine
from sqlalchemy.exc import IntegrityError, OperationalError

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
  text VARCHAR(17) NOT NULL, 
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
  a VARCHAR(1) NOT NULL, 
  b VARCHAR(2) NOT NULL, 
  c VARCHAR(3) NOT NULL, 
  d VARCHAR(4) NOT NULL, 
  e VARCHAR(4) NOT NULL, 
  f VARCHAR(1) NOT NULL
);
''')  # noqa

    def test_no_inference(self):
        sql = self.get_output(['--tables', 'foo', '--no-inference', 'examples/testfixed_converted.csv'])

        self.assertEqual(sql.replace('\t', '  '), '''CREATE TABLE foo (
  text VARCHAR(17) NOT NULL, 
  date VARCHAR(10), 
  integer VARCHAR(3), 
  boolean VARCHAR(5), 
  float VARCHAR(11), 
  time VARCHAR(8), 
  datetime VARCHAR(19), 
  empty_column VARCHAR(1)
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
            sql = self.get_output(['--query', 'SELECT m.usda_id, avg(i.sepal_length) AS mean_sepal_length FROM iris AS i JOIN irismeta AS m ON (i.species = m.species) GROUP BY m.species', 'examples/iris.csv', 'examples/irismeta.csv'])

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
        sql = self.get_output(['--insert', '--query', 'SELECT text FROM testfixed_converted WHERE text LIKE "Chicago%"', 'examples/testfixed_converted.csv'])

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

    def test_prefix(self):
        self.get_output(['--insert', '--db', 'sqlite:///' + self.db_file, 'examples/dummy.csv'])

        engine = create_engine('sqlite:///' + self.db_file)
        connection = engine.connect()
        metadata = MetaData(connection)
        table = Table('dummy', metadata, autoload=True, autoload_with=connection)
        index = Index('myindex', table.c.a, unique=True)
        index.create(bind=connection)

        self.get_output(['--prefix', 'OR IGNORE', '--no-create', '--insert', '--db', 'sqlite:///' + self.db_file, 'examples/dummy.csv'])

    def test_query_with_unique_constraint(self):
        self.get_output(['--insert', '--tables', 'foo', '--db', 'sqlite:///' + self.db_file, 'examples/foo1.csv', '--unique-constraint', 'id'])
        with self.assertRaises(IntegrityError):
            self.get_output(['--insert', '--tables', 'foo', '--db', 'sqlite:///' + self.db_file, 'examples/foo1.csv', '--no-create'])

    def test_no_create_if_not_exists(self):
        self.get_output(['--insert', '--tables', 'foobad', '--db', 'sqlite:///' + self.db_file, 'examples/foo1.csv'])
        with self.assertRaises(OperationalError):
            self.get_output(['--insert', '--tables', 'foobad', '--db', 'sqlite:///' + self.db_file, 'examples/foo2.csv'])

    def test_create_if_not_exists(self):
        self.get_output(['--insert', '--tables', 'foo', '--db', 'sqlite:///' + self.db_file, 'examples/foo1.csv'])
        self.get_output(['--insert', '--tables', 'foo', '--db', 'sqlite:///' + self.db_file, 'examples/foo2.csv', '--create-if-not-exists'])
