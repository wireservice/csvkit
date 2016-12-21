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
        self.assertEqual('i_work_here', match_column_identifier(self.headers, 'i_work_here'))
        self.assertEqual('i_work_here', match_column_identifier(self.headers, 'i_work_here', column_offset=0))

    def test_match_column_identifier_numeric(self):
        self.assertEqual('i_work_here', match_column_identifier(self.headers, 3))
        self.assertEqual('1', match_column_identifier(self.headers, 3, column_offset=0))

    def test_match_column_which_could_be_integer_name_is_treated_as_positional_id(self):
        self.assertEqual('id', match_column_identifier(self.headers, '1'))
        self.assertEqual('name', match_column_identifier(self.headers, '1', column_offset=0))

    def test_parse_column_identifiers(self):
        self.assertEqual(['i_work_here', 'id', 'name'], parse_column_identifiers('i_work_here,1,name', self.headers))
        self.assertEqual(['i_work_here', 'name', 'name'], parse_column_identifiers('i_work_here,1,name', self.headers, column_offset=0))

    def test_range_notation(self):
        self.assertEqual(['id', 'name', 'i_work_here'], parse_column_identifiers('1:3', self.headers))
        self.assertEqual(['name', 'i_work_here', '1'], parse_column_identifiers('1:3', self.headers, column_offset=0))
        self.assertEqual(['name', 'i_work_here', '1'], parse_column_identifiers('2-4', self.headers))
        self.assertEqual(['i_work_here', '1', 'more-header-values'], parse_column_identifiers('2-4', self.headers, column_offset=0))
        self.assertEqual(['id', 'name', 'i_work_here', '1'], parse_column_identifiers('1,2:4', self.headers))
        self.assertEqual(['name', 'i_work_here', '1', 'more-header-values'], parse_column_identifiers('1,2:4', self.headers, column_offset=0))
        self.assertEqual(['more-header-values', 'i_work_here', 'stuff'], parse_column_identifiers('more-header-values,3,stuff', self.headers))
        self.assertEqual(['more-header-values', '1', 'stuff'], parse_column_identifiers('more-header-values,3,stuff', self.headers, column_offset=0))

    def test_range_notation_open_ended(self):
        self.assertEqual(['id', 'name', 'i_work_here'], parse_column_identifiers(':3', self.headers))

        target = [self.headers[0]] + self.headers[3:]
        self.assertEqual(target, parse_column_identifiers('1,4:', self.headers))

        self.assertEqual(self.headers, parse_column_identifiers('1:', self.headers))
