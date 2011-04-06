#!/usr/bin/env python

import datetime
import unittest

from csvkit import sql
from csvkit import typeinference

from sqlalchemy import Column
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time

class TestSQL(unittest.TestCase):
    def test_make_column_name(self):
        c = sql.make_column('test', int, [1, -87, 418000000, None])
        self.assertEqual(c.key, 'test')

    def test_make_column_bool(self):
        c = sql.make_column('test', bool, [True, True, False, None])
        self.assertEqual(type(c.type), Boolean)

    def test_make_column_int(self):
        c = sql.make_column('test', int, [1, -87, 418000000, None])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)

    def test_make_column_float(self):
        c = sql.make_column('test', float, [1.01, -87.34, 418000000.0, None])
        self.assertEqual(type(c.type), Float)

    def test_make_column_datetime(self):
        c = sql.make_column('test', datetime.datetime, [datetime.datetime(2010, 04, 05, 20, 42, 0), datetime.datetime(1910, 04, 05, 20, 37, 21), None])
        self.assertEqual(type(c.type), DateTime)

    def test_make_column_date(self):
        c = sql.make_column('test', datetime.date, [datetime.date(2010, 04, 05), datetime.datetime(1910, 04, 05), None])
        self.assertEqual(type(c.type), Date)

    def test_make_column_time(self):
        c = sql.make_column('test', datetime.time, [datetime.time(20, 42, 0), datetime.time(20, 37, 21), None])
        self.assertEqual(type(c.type), Time)

    def test_make_column_null(self):
        c = sql.make_column('test', str, [None, None, None])
        self.assertEqual(type(c.type), String)

    def test_make_column_string(self):
        c = sql.make_column('test', str, ['this', 'is', 'test', 'data'])
        self.assertEqual(type(c.type), String)

    def test_column_nullable(self):
        c = sql.make_column('test', int, [1, -87, 418000000, None])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)
        self.assertEqual(c.nullable, True)

    def test_column_not_nullable(self):
        c = sql.make_column('test', int, [1, -87, 418000000])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)
        self.assertEqual(c.nullable, False)

    def test_make_create_table_statement(self):
        pass

