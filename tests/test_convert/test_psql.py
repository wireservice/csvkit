#!/usr/bin/env python

import unittest

from csvkit.convert import psql

class TestPSQL(unittest.TestCase):
    def test_psql(self):
        with open('examples/test_psql_cities.txt') as f:
            output = psql.psql2csv(f)

        with open('examples/test_psql_cities.csv') as f:
            self.assertEquals(f.read(), output)

