#!/usr/bin/env python

import unittest

from csvkit import join
from csvkit import table

class TestJoin(unittest.TestCase):
    def setUp(self):
        self.tab1 = table.Table([
            table.Column(0, 'id', [u'1', u'2', u'3']),
            table.Column(1, 'name', [u'Chicago Reader', u'Chicago Sun-Times', u'Chicago Tribune']),
            table.Column(2, 'i_work_here', [u'0', u'0', u'1'])])

        self.tab2 = table.Table([
            table.Column(0, 'id', [u'1', u'2', u'4']),
            table.Column(1, 'age', [u'40', u'63', u'5']),
            table.Column(2, 'i_work_here', [u'0', u'0', u'0', u'0'])]) # Not extra value in this column

    def test_inner_join(self):
        jointab = table.Table()
        jointab.extend(self.tab1)
        join.inner_join(jointab, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(tab1) + len(tab2) - 1)
        self.assertEqual(jointab.headers(), [u'id', u'name', u'i_work_here', u'age', u'i_work_here2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row_count, 2)

    def test_full_outer_join(self):
        jointab = table.Table()
        jointab.extend(self.tab1)
        join.full_outer_join(jointab, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(tab1) + len(tab2) - 1)
        self.assertEqual(jointab.headers(), [u'id', u'name', u'i_work_here', u'age', u'i_work_here2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [3, u'Chicago Tribune', True, None, None])
        self.assertEqual(jointab.row(3), [4, None, None, 5, False])
        self.assertEqual(jointab.row_count, 4)

    def test_left_outer_join(self):
        jointab = table.Table()
        jointab.extend(self.tab1)
        join.left_outer_join(jointab, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(tab1) + len(tab2) - 1)
        self.assertEqual(jointab.headers(), [u'id', u'name', u'i_work_here', u'age', u'i_work_here2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [3, u'Chicago Tribune', True, None, None])
        self.assertEqual(jointab.row_count, 3)

    def test_right_outer_join(self):
        jointab = table.Table()
        jointab.extend(self.tab1)
        join.right_outer_join(jointab, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(tab1) + len(tab2) - 1)
        self.assertEqual(jointab.headers(), [u'id', u'name', u'i_work_here', u'age', u'i_work_here2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [4, None, None, 5, False])
        self.assertEqual(jointab.row_count, 3)
