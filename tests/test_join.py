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
        jointab = join.inner_join(self.tab1, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(self.tab1) + len(self.tab2) - 1)
        self.assertEqual(jointab.headers(), ['id', 'name', 'i_work_here', 'age', 'i_work_here_2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row_count, 2)

    def test_full_outer_join(self):
        jointab = join.full_outer_join(self.tab1, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(self.tab1) + len(self.tab2) - 1)
        self.assertEqual(jointab.headers(), ['id', 'name', 'i_work_here', 'age', 'i_work_here_2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [3, u'Chicago Tribune', True, None, None])
        self.assertEqual(jointab.row(3), [4, None, None, 5, False])
        self.assertEqual(jointab.row_count, 4)

    def test_left_outer_join(self):
        jointab = join.left_outer_join(self.tab1, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(self.tab1) + len(self.tab2) - 1)
        self.assertEqual(jointab.headers(), ['id', 'name', 'i_work_here', 'age', 'i_work_here_2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [3, u'Chicago Tribune', True, None, None])
        self.assertEqual(jointab.row_count, 3)

    def test_right_outer_join(self):
        jointab = join.right_outer_join(self.tab1, 'id', self.tab2, 'id')
        self.assertEqual(len(jointab), len(self.tab1) + len(self.tab2) - 1)
        self.assertEqual(jointab.headers(), ['id', 'name', 'i_work_here', 'age', 'i_work_here_2'])
        self.assertEqual(jointab.row(0), [1, u'Chicago Reader', False, 40, False])
        self.assertEqual(jointab.row(2), [4, None, None, 5, False])
        self.assertEqual(jointab.row_count, 3)
