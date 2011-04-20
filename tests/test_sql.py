#!/usr/bin/env python

import unittest

from csvkit import sql
from csvkit import table

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time

class TestSQL(unittest.TestCase):
    def setUp(self):
        self.csv_table = table.Table([
            table.Column(0, u'text', [u'Chicago Reader', u'Chicago Sun-Times', u'Chicago Tribune', u'Row with blanks']),
            table.Column(1, u'integer', [u'40', u'63', u'164', u'']),
            table.Column(2, u'datetime', [u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', '']),
            table.Column(3, u'empty_column', [u'', u'', u'', u''])],
            name='test_table')

    def test_make_column_name(self):
        c = sql.make_column(table.Column(0, 'test', ['1', '-87', '418000000', '']))
        self.assertEqual(c.key, 'test')

    def test_make_column_bool(self):
        c = sql.make_column(table.Column(0, 'test', ['True', 'True', 'False', '']))
        self.assertEqual(type(c.type), Boolean)

    def test_make_column_int(self):
        c = sql.make_column(table.Column(0, 'test', ['1', '-87', '418000000', '']))
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)

    def test_make_column_float(self):
        c = sql.make_column(table.Column(0, 'test', ['1.01', '-87.34', '418000000.0', '']))
        self.assertEqual(type(c.type), Float)

    def test_make_column_datetime(self):
        c = sql.make_column(table.Column(0, 'test', [u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', '']))
        self.assertEqual(type(c.type), DateTime)

    def test_make_column_date(self):
        c = sql.make_column(table.Column(0, 'test', ['Jan 1, 2008', '2010-01-27', '3/1/08', '']))
        self.assertEqual(type(c.type), Date)

    def test_make_column_time(self):
        c = sql.make_column(table.Column(0, 'test', ['4:40 AM', '03:45:00', '16:14:45', '']))
        self.assertEqual(type(c.type), Time)

    def test_make_column_null(self):
        c = sql.make_column(table.Column(0, 'test', ['', '', '']))
        self.assertEqual(type(c.type), String)

    def test_make_column_string(self):
        c = sql.make_column(table.Column(0, 'test', ['this', 'is', 'test', 'data']))
        self.assertEqual(type(c.type), String)

    def test_make_column_string_length(self):
        c = sql.make_column(table.Column(0, 'test', ['this', 'is', 'test', 'data', 'that', 'is', 'awesome']))
        self.assertEqual(c.type.length, 7)
    
    def test_column_nullable(self):
        c = sql.make_column(table.Column(0, 'test', ['1', '-87', '418000000', '']))
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)
        self.assertEqual(c.nullable, True)

    def test_column_not_nullable(self):
        c = sql.make_column(table.Column(0, 'test', ['1', '-87', '418000000']))
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)
        self.assertEqual(c.nullable, False)

    def test_make_create_table_statement(self):
        sql_table = sql.make_table(self.csv_table, 'csvsql')
        statement = sql.make_create_table_statement(sql_table)

        self.assertEqual(statement, 
u"""CREATE TABLE test_table (
\ttext VARCHAR(17) NOT NULL, 
\tinteger INTEGER, 
\tdatetime DATETIME, 
\tempty_column VARCHAR(32)
);""")

    def make_insert_statement(self):
        sql_table = sql.make_table(self.csv_table, 'csvsql')
        statement = sql.make_insert_statement(sql_table, self.csv_table._prepare_rows_for_serialization()[0])
        self.assertEqual(statement, u'INSERT INTO test_table (text, integer, datetime, empty_column) VALUES (\'Chicago Reader\', 40, \'2008-01-01T04:40:00\', NULL);')

