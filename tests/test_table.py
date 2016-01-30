#!/usr/bin/env python

import datetime

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import table


class TestColumn(unittest.TestCase):

    def setUp(self):
        self.c = table.Column(0, u'test', [u'test', u'column', None])
        self.c2 = table.Column(0, u'test', [0, 1, 42], normal_type=int)
        self.c3 = table.Column(0, u'test', [datetime.datetime(2007, 1, 1, 12, 13, 14)], normal_type=datetime.datetime)

    def test_create_column(self):
        self.assertEqual(type(self.c), table.Column)
        self.assertEqual(self.c.order, 0)
        self.assertEqual(self.c.name, u'test')
        self.assertEqual(self.c.type, six.text_type)
        self.assertEqual(self.c, [u'test', u'column', None])

    def test_slice(self):
        self.assertEqual(self.c[1:], [u'column', None])

    def test_access(self):
        self.assertEqual(self.c[-1], None)

    def test_out_of_bounds(self):
        self.assertEqual(self.c[27], None)

    def test_has_nulls(self):
        self.assertEqual(self.c.has_nulls(), True)

    def test_no_null(self):
        self.assertEqual(self.c2.has_nulls(), False)

    def test_max_length(self):
        self.assertEqual(self.c.max_length(), 6)
        self.assertEqual(self.c2.max_length(), 0)
        self.assertEqual(self.c3.max_length(), 0)


class TestTable(unittest.TestCase):

    def test_from_csv(self):
        with open('examples/testfixed_converted.csv', 'r') as f:
            t = table.Table.from_csv(f)

        self.assertEqual(type(t), table.Table)
        self.assertEqual(type(t[0]), table.Column)
        self.assertEqual(len(t), 8)

        self.assertEqual(t[2][0], 40)
        self.assertEqual(type(t[2][0]), int)

        self.assertEqual(t[3][0], True)
        self.assertEqual(type(t[3][0]), bool)

    def test_extra_header(self):
        with open('examples/test_extra_header.csv', 'r') as f:
            t = table.Table.from_csv(f)

        self.assertEqual(type(t), table.Table)
        self.assertEqual(type(t[0]), table.Column)
        self.assertEqual(len(t), 4)

        self.assertEqual(t[0], [1])
        self.assertEqual(t[1], [2])
        self.assertEqual(t[2], [3])
        self.assertEqual(t[3], [None])

    def test_from_csv_no_inference(self):
        with open('examples/testfixed_converted.csv', 'r') as f:
            t = table.Table.from_csv(f, infer_types=False)

        self.assertEqual(type(t), table.Table)
        self.assertEqual(type(t[0]), table.Column)
        self.assertEqual(len(t), 8)

        self.assertEqual(t[2][0], '40')
        self.assertEqual(type(t[2][0]), six.text_type)

        self.assertEqual(t[3][0], 'True')
        self.assertEqual(type(t[3][0]), six.text_type)

    def test_from_csv_empty_file(self):
        table.Table.from_csv(six.StringIO('\n\n'))

    def test_from_csv_dev_null(self):
        with open('/dev/null', 'r') as f:
            table.Table.from_csv(f)

    def test_table_count_rows(self):
        c = table.Column(0, u'test', [u'test', u'column', u''])
        c_short = table.Column(0, u'test', [u'test'])
        c_long = table.Column(0, u'test', [u'', u'', u'', u''])
        t = table.Table()
        self.assertEqual(t.count_rows(), 0)
        t.append(c)
        self.assertEqual(t.count_rows(), 3)
        t.append(c_short)
        self.assertEqual(t.count_rows(), 3)
        t.append(c_long)
        self.assertEqual(t.count_rows(), 4)
