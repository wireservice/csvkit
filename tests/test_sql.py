#!/usr/bin/env python

import datetime
import unittest

from csvkit import sql
from csvkit import typeinference

from sqlalchemy import Column
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time

class TestSQL(unittest.TestCase):
    def test_make_column_bool(self):
        c = sql.make_column('test', bool, [True, True, False])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Boolean)
        self.assertEqual(c.nullable, False)

    def test_make_column_int(self):
        c = sql.make_column('test', int, [1, -87, 418000000, None])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Integer)
        self.assertEqual(c.nullable, True)

    def test_make_column_float(self):
        c = sql.make_column('test', float, [1.01, -87.34, 418000000.0])
        self.assertEqual(c.key, 'test')
        self.assertEqual(type(c.type), Float)
        self.assertEqual(c.nullable, False)

    def test_make_column_datetime(self):
        pass

    def test_make_column_date(self):
        pass

    def test_make_column_time(self):
        pass

    def test_make_column_null(self):
        pass

    def test_make_column_string(self):
        pass

    def test_make_create_table_statement(self):
        pass
