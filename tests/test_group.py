#!/usr/bin/env python

import unittest
from csvkit.group import group_rows, MaxAggregator, MinAggregator, CountAggregator, CountAAggregator, SumAggregator

test_header = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
test_data = [['a', 'a', 'a', 1, 2, 3],
             ['b', 'a', 'a', 3, 2, 1],
             ['c', 'b', 'a', 0, 0, 0],
             ['d', 'b', 'a', 6, 7, 1]]


class TestAggregators(unittest.TestCase):
    def test_max(self):
        a = MaxAggregator(3)
        for row in test_data:
            a.take_row(row)
        self.assertEqual(a.get_result(), 6)


    def test_min(self):
        a = MinAggregator(3)
        for row in test_data:
            a.take_row(row)
        self.assertEqual(a.get_result(), 0)

    def test_sum(self):
        a = SumAggregator(3)
        for row in test_data:
            a.take_row(row)
        self.assertEqual(a.get_result(), 10)

    def test_count(self):
        a = CountAggregator(3)
        for row in test_data:
            a.take_row(row)
        self.assertEqual(a.get_result(), 4)

    def test_countA(self):
        a = CountAAggregator(3)
        for row in test_data:
            a.take_row(row)
        self.assertEqual(a.get_result(), 3)


class TestGroup(unittest.TestCase):
    def test_header(self):
        output = list(group_rows(test_header, test_data, [1],
                                 [MaxAggregator(3), MinAggregator(4)]))
        self.assertEqual(output[0], ['h2', 'max(h4)', 'min(h5)'])


    def test_group_zero(self):
        output = list(group_rows(test_header, test_data, [],
                                 [MaxAggregator(3), MinAggregator(4),
                                  CountAggregator(4), ]))
        self.assertEqual(len(output), 2)
        self.assertEqual(output[1], [6, 0, 4])

    def test_group_one(self):
        output = list(group_rows(test_header, test_data, [1],
                                 [MaxAggregator(3), MinAggregator(4),
                                  CountAggregator(4), ]))
        self.assertEqual(len(output), 3)
        self.assertEqual(output[1], ['a', 3, 2, 2])
        self.assertEqual(output[2], ['b', 6, 0, 2])


    def test_group_two(self):
        output = list(group_rows(test_header, test_data, [1, 2],
                                 [MaxAggregator(3), MinAggregator(4),
                                  CountAggregator(4), ]))
        self.assertEqual(len(output), 3)
        self.assertEqual(output[1], ['a', 'a', 3, 2, 2])
        self.assertEqual(output[2], ['b', 'a', 6, 0, 2])



