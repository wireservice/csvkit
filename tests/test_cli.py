#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.cli import match_column_identifier, parse_column_identifiers


class TestCli(unittest.TestCase):

    def setUp(self):
        self.headers = ['id', 'name', 'i_work_here', '1', 'more-header-values', 'stuff', 'blueberry']

    def test_match_column_identifier_string(self):
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here'))
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here', column_offset=0))

    def test_match_column_identifier_numeric(self):
        self.assertEqual(2, match_column_identifier(self.headers, 3))
        self.assertEqual(3, match_column_identifier(self.headers, 3, column_offset=0))

    def test_match_column_which_could_be_integer_name_is_treated_as_positional_id(self):
        self.assertEqual(0, match_column_identifier(self.headers, '1'))
        self.assertEqual(1, match_column_identifier(self.headers, '1', column_offset=0))

    def test_parse_column_identifiers(self):
        self.assertEqual([2, 0, 1], parse_column_identifiers('i_work_here,1,name', self.headers))
        self.assertEqual([2, 1, 1], parse_column_identifiers('i_work_here,1,name', self.headers, column_offset=0))

    def test_range_notation(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers('1:3', self.headers))
        self.assertEqual([1, 2, 3], parse_column_identifiers('1:3', self.headers, column_offset=0))
        self.assertEqual([1, 2, 3], parse_column_identifiers('2-4', self.headers))
        self.assertEqual([2, 3, 4], parse_column_identifiers('2-4', self.headers, column_offset=0))
        self.assertEqual([0, 1, 2, 3], parse_column_identifiers('1,2:4', self.headers))
        self.assertEqual([1, 2, 3, 4], parse_column_identifiers('1,2:4', self.headers, column_offset=0))
        self.assertEqual([4, 2, 5], parse_column_identifiers('more-header-values,3,stuff', self.headers))
        self.assertEqual([4, 3, 5], parse_column_identifiers('more-header-values,3,stuff', self.headers, column_offset=0))

    def test_range_notation_open_ended(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers(':3', self.headers))

        target = list(range(3, len(self.headers)))  # protect against devs adding to self.headers
        target.insert(0, 0)
        self.assertEqual(target, parse_column_identifiers('1,4:', self.headers))

        self.assertEqual(list(range(0, len(self.headers))), parse_column_identifiers('1:', self.headers))
