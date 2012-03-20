#!/usr/bin/env python

import unittest

from csvkit.group import group_rows
import csvkit.utilities.csvgroup  # At least verify this imports


class TestGroup(unittest.TestCase):

    def setUp(self):
        self.header = ['h1', 'h2', 'h3']
        self.tab1 = [
            ['a', 'a', 'a'],
            ['b', 'a', 'a'],
            ['c', 'b', 'a'],
            ['d', 'b', 'a']]

    def test_header(self):
        output = group_rows(self.header, self.tab1, [0])
        self.assertEqual(output[0], ['h1', 'h2', 'h3'])

    def test_header_with_count(self):
        #Note: arguments to group_rows are zero indexed, unlike on command line
        output = group_rows(self.header, self.tab1, [0], 'count')
        self.assertEqual(output[0], ['h1', 'h2', 'h3', 'count'])

    def test_group_one(self):
        output = group_rows(self.header, self.tab1, [2], 'count')
        self.assertEqual(len(output), 2)
        self.assertEqual(output[1], ['a', 'a', 'a', 4])

    def test_group_two(self):
        output = group_rows(self.header, self.tab1, [1], 'count')
        self.assertEqual(len(output), 3)
        self.assertEqual(output[1], ['a', 'a', 'a', 2])
        self.assertEqual(output[2], ['c', 'b', 'a', 2])

    def test_group_two_columns_unique(self):
        output = group_rows(self.header, self.tab1, [0, 1], 'count')
        self.assertEqual(len(output), 5)
        self.assertEqual(output[1], ['a', 'a', 'a', 1])
        self.assertEqual(output[2], ['b', 'a', 'a', 1])
        self.assertEqual(output[3], ['c', 'b', 'a', 1])
        self.assertEqual(output[4], ['d', 'b', 'a', 1])

    def test_group_two_columns_non_unique(self):
        output = group_rows(self.header, self.tab1, [1, 2], 'count')
        self.assertEqual(len(output), 3)
        self.assertEqual(output[1], ['a', 'a', 'a', 2])
        self.assertEqual(output[2], ['c', 'b', 'a', 2])

    def test_group_two_group_only(self):
        output = group_rows(self.header, self.tab1, [1, 2], 'count', grouped_only=True)
        self.assertEqual(len(output), 3)
        self.assertEqual(output[1], ['a', 'a', 2])
        self.assertEqual(output[2], ['b', 'a', 2])
