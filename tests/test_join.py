#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import join

class TestJoin(unittest.TestCase):
    def setUp(self):
        self.tab1 = [
            ['id', 'name', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first'],
            [u'2', u'Chicago Sun-Times', u'only'],
            [u'3', u'Chicago Tribune', u'only'],
            [u'1', u'Chicago Reader', u'second']]

        self.tab2 = [
            ['id', 'age', 'i_work_here'],
            [u'1', u'first', u'0'],
            [u'4', u'only', u'0'],
            [u'1', u'second', u'0'],
            [u'2', u'only', u'0', u'0']] # Note extra value in this column

    def test_get_ordered_keys(self):
        self.assertEqual(join._get_ordered_keys(self.tab1[1:], 0), [u'1', u'2', u'3', u'1'])
        self.assertEqual(join._get_ordered_keys(self.tab2[1:], 0), [u'1', u'4', u'1', u'2'])

    def test_get_mapped_keys(self):
        self.assertEqual(join._get_mapped_keys(self.tab1[1:], 0), {
            u'1': [[u'1', u'Chicago Reader', u'first'], [u'1', u'Chicago Reader', u'second']],
            u'2': [[u'2', u'Chicago Sun-Times', u'only']],
            u'3': [[u'3', u'Chicago Tribune', u'only']]})

    def test_sequential_join(self):
        self.assertEqual(join.sequential_join(self.tab1, self.tab2), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'4', u'only', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'1', u'second', u'0'],
            [u'1', u'Chicago Reader', u'second', u'2', u'only', u'0', u'0']])

    def test_inner_join(self):
        self.assertEqual(join.inner_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0']])

    def test_full_outer_join(self):
        self.assertEqual(join.full_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'', u'', u''],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0'],
            [u'', u'', u'', u'4', u'only', u'0']])

    def test_left_outer_join(self):
        self.assertEqual(join.left_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'', u'', u''],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0']])

    def test_right_outer_join(self):
        self.assertEqual(join.right_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0'],
            [u'', u'', u'', u'4', u'only', u'0']])
