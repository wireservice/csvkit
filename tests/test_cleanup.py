#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.cleanup import join_rows


class TestCleanup(unittest.TestCase):

    def test_fix_rows(self):
        """Test to ensure that row merging yields correct results"""
        start = [['1', '2', '3', ],
                 [''],
                 ['abc'],
                 ['4', '5']
                 ]
        fixed = join_rows(start)
        self.assertEqual(4, len(fixed))
        self.assertEqual(start[0][0], fixed[0])
        self.assertEqual(start[0][1], fixed[1])
        self.assertEqual(" ".join([start[0][-1], start[1][0], start[2][0], start[3][0]]), fixed[2])
        self.assertEqual(start[3][1], fixed[3])

    def test_real_world_join_fail(self):
        start = [['168772', '1102', '$0.23 TO $0.72', 'HOUR', '1.5%'],
                 ['GROSS', '1.5% '],
                 ['GROSS', '430938']]
        fixed = join_rows(start)
        self.assertEqual(7, len(fixed))
        self.assertEqual(start[0][0], fixed[0])
        self.assertEqual(start[0][1], fixed[1])
        self.assertEqual(start[0][2], fixed[2])
        self.assertEqual(start[0][3], fixed[3])
        expected4 = " ".join([start[0][-1], start[1][0]])
        self.assertEqual(expected4, fixed[4])
        expected5 = " ".join([start[1][1], start[2][0]])
        self.assertEqual(expected5, fixed[5])
        self.assertEqual(start[2][1], fixed[6])
