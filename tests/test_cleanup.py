#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.cleanup import extract_joinable_row_errors, join_rows
from csvkit.exceptions import CSVTestException, LengthMismatchError


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

    def test_extract_joinable_row_errors(self):
        e1 = LengthMismatchError(1, ['foo', 'bar', 'baz'], 10)
        e2 = LengthMismatchError(2, ['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatchError(3, ['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(3, len(joinable))
        for e, j in zip(errs, joinable):
            self.assertTrue(e is j)

    def test_extract_joinable_row_errors_2(self):
        e1 = LengthMismatchError(1, ['foo', 'bar', 'baz'], 10)
        e2 = CSVTestException(2, ['foo', 'bar', 'baz'], "A throwaway message.")
        e3 = LengthMismatchError(3, ['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(1, len(joinable))
        self.assertTrue(next(iter(joinable)) is e3)

    def test_extract_joinable_row_errors_3(self):
        e1 = CSVTestException(1, ['foo', 'bar', 'baz'], "A throwaway message.")
        e2 = LengthMismatchError(2, ['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatchError(3, ['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(2, len(joinable))
        joinable = list(joinable)
        self.assertTrue(joinable[0] is e2)
        self.assertTrue(joinable[1] is e3)

    def test_extract_joinable_row_errors_4(self):
        e1 = CSVTestException(1, ['foo', 'bar', 'baz'], "A throwaway message.")
        e2 = LengthMismatchError(2, ['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatchError(4, ['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(1, len(joinable))
        self.assertTrue(next(iter(joinable)) is e3)

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
