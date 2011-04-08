#!/usr/bin/env python

import datetime
import unittest

from csvkit import sql
from csvkit import table

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time

class TestSQL(unittest.TestCase):
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
        csv_table = table.Table(['text', 'integer', 'datetime', 'empty_column'], [
            table.Column(0, 'text', ['Chicago Reader', 'Chicago Sun-Times', 'Chicago Tribune', 'Row with blanks']),
            table.Column(1, 'integer', ['40', '63', '164', '']),
            table.Column(2, 'datetime', ['Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', '']),
            table.Column(3, 'empty_column', ['', '', '', ''])])

        sql_table = sql.make_table(csv_table, 'csvsql')
        statement = sql.make_create_table_statement(sql_table)

        self.assertEqual(statement, 
u"""CREATE TABLE csvsql (
\ttext VARCHAR(17) NOT NULL, 
\tinteger INTEGER, 
\tdatetime DATETIME, 
\tempty_column VARCHAR(32)
)""")



