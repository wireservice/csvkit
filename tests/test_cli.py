#!/usr/bin/env python

import unittest

from csvkit.cli import match_column_identifier, parse_column_identifiers

class TestCli(unittest.TestCase):
    def setUp(self):
        self.headers = ['id', 'name', 'i_work_here', '1']

    def test_match_column_identifier_string(self):
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here'))

    def test_match_column_identifier_numeric(self):
        self.assertEqual(2, match_column_identifier(self.headers, 3))

    def test_match_column_which_could_be_integer_name_is_treated_as_positional_id(self):
        self.assertEqual(0, match_column_identifier(self.headers, '1'))

    def test_parse_column_identifiers(self):
        self.assertEqual([2, 0, 1], parse_column_identifiers(' i_work_here, 1,name  ', self.headers))
