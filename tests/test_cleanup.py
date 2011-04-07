import unittest

from csvkit.cleanup import *

class TestNormalizeType(unittest.TestCase):
    def test_fix_rows(self):
        """Test to ensure that row merging yields correct results"""
        start = [['1', '2', '3',],
                 [''],
                 ['abc'],
                 ['4', '5']
                ]
        fixed = join_rows(start)
        self.assertEqual(4,len(fixed))
        self.assertEqual(start[0][0],fixed[0])
        self.assertEqual(start[0][1],fixed[1])
        self.assertEqual("\n".join([start[0][-1], start[1][0], start[2][0], start[3][0]]),fixed[2])
        self.assertEqual(start[3][1],fixed[3])

    def test_fix_length_errors_basic(self):
        expected_length = 4
        errs = [LengthMismatch(1,['alpha','beta','gam'],expected_length)]
        errs.append(LengthMismatch(2,['ma','delta'],expected_length))
        fixed = fix_length_errors(errs,expected_length)
        self.assertEqual(1,len(fixed))
        fixed = fixed[0]
        self.assertEqual('alpha',fixed[0])
        self.assertEqual('beta',fixed[1])
        self.assertEqual('gam\nma',fixed[2])
        self.assertEqual('delta',fixed[3])

    def test_extract_joinable_row_errors(self):
        e1 = LengthMismatch(1,['foo', 'bar', 'baz'], 10)
        e2 = LengthMismatch(2,['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatch(3,['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(3,len(joinable))
        for e, j in zip(errs, joinable):
            self.assertTrue(e is j)

    def test_extract_joinable_row_errors_2(self):
        e1 = LengthMismatch(1,['foo', 'bar', 'baz'], 10)
        e2 = CSVTestException(2,['foo', 'bar', 'baz'], "A throwaway message.")
        e3 = LengthMismatch(3,['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(1,len(joinable))
        self.assertTrue(iter(joinable).next() is e3)


    def test_extract_joinable_row_errors_3(self):
        e1 = CSVTestException(1,['foo', 'bar', 'baz'], "A throwaway message.")
        e2 = LengthMismatch(2,['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatch(3,['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(2,len(joinable))
        self.assertTrue(iter(joinable).next() is e2)
        self.assertTrue(iter(joinable).next() is e3)


    def test_extract_joinable_row_errors_3(self):
        e1 = CSVTestException(1,['foo', 'bar', 'baz'], "A throwaway message.")
        e2 = LengthMismatch(2,['foo', 'bar', 'baz'], 10)
        e3 = LengthMismatch(4,['foo', 'bar', 'baz'], 10)
        errs = [e1, e2, e3]
        joinable = extract_joinable_row_errors(errs)
        self.assertEqual(1,len(joinable))
        self.assertTrue(iter(joinable).next() is e3)

