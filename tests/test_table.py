#!/usr/bin/env python

from cStringIO import StringIO
import unittest

from csvkit import table 

class TestColumn(unittest.TestCase):
    def setUp(self):
        self.c = table.Column(0, u'test', [u'test', u'column', None])

    def test_create_column(self):
        self.assertEqual(type(self.c), table.Column)
        self.assertEqual(self.c.index, 0)
        self.assertEqual(self.c.name, u'test')
        self.assertEqual(self.c.type, unicode)
        self.assertEqual(self.c, [u'test', u'column', None])

    def test_slice(self):
        self.assertEqual(self.c[1:], [u'column', None])

    def test_access(self):
        self.assertEqual(self.c[-1], None)

class TestTable(unittest.TestCase):
    def test_from_csv(self):
        with open('examples/testfixed_converted.csv', 'r') as f:
            t = table.Table.from_csv(f)

        self.assertEqual(type(t), table.Table)
        self.assertEqual(type(t[0]), table.Column)
        self.assertEqual(len(t), 8)

    def test_to_csv(self):
        with open('examples/testfixed_converted.csv', 'r') as f:
            contents = f.read()
            f.seek(0)
            o = StringIO()
            table.Table.from_csv(f).to_csv(o)
            conversion = o.getvalue()
            o.close()
        
        self.assertEqual(contents, conversion)

    def test_table_append(self):
        c = table.Column(0, u'test', [u'test', u'column', None])
        t = table.Table()
        t.append(c)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0], c)

    def test_table_insert(self):
        c = table.Column(0, u'test', [u'test', u'column', None])
        c2 = table.Column(0, u'test', [u'test', u'column', None])
        t = table.Table([c])
        t.insert(0, c2)
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0], c2)
        self.assertEqual(t[1], c)
        self.assertEqual(t[0].index, 0)
        self.assertEqual(t[1].index, 1)

    def test_table_extend(self):
        c = table.Column(0, u'test', [u'test', u'column', None])
        c2 = table.Column(0, u'test', [u'test', u'column', None])
        c3 = table.Column(0, u'test', [u'test', u'column', None])
        t = table.Table([c])
        t.extend([c2, c3])
        self.assertEqual(len(t), 3)
        self.assertEqual(t[0], c)
        self.assertEqual(t[1], c2)
        self.assertEqual(t[2], c3)
        self.assertEqual(t[0].index, 0)
        self.assertEqual(t[1].index, 1)
        self.assertEqual(t[2].index, 2)

    def test_table_remove(self):
        c = table.Column(0, u'test', [u'test', u'column', None])
        c2 = table.Column(0, u'test', [u'test', u'column', None])
        c3 = table.Column(0, u'test', [u'test', u'column', None])
        t = table.Table([c, c2, c3])
        t.remove(c2)
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0], c)
        self.assertEqual(t[1], c3)
        self.assertEqual(t[0].index, 0)
        self.assertEqual(t[1].index, 1)

    def test_table_sort(self):
        t = table.Table()
        self.assertRaises(NotImplementedError, t.sort)

    def test_table_reverse(self):
        t = table.Table()
        self.assertRaises(NotImplementedError, t.reverse)
