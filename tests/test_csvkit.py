#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
import unittest

import csvkit

class TestCSVKitReader(unittest.TestCase):
    def test_utf8(self):
        with open('examples/test_utf8.csv') as f:
            reader = csvkit.CSVKitReader(f, encoding='utf-8')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

    def test_reader_alias(self):
        with open('examples/test_utf8.csv') as f:
            reader = csvkit.reader(f, encoding='utf-8')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'ʤ'])


class TestCSVKitWriter(unittest.TestCase):
    def test_utf8(self):
        output = StringIO()
        writer = csvkit.CSVKitWriter(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = StringIO(output.getvalue())

        reader = csvkit.CSVKitReader(written, encoding='utf-8')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

    def test_writer_alias(self):
        output = StringIO()
        writer = csvkit.writer(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = StringIO(output.getvalue())

        reader = csvkit.reader(written, encoding='utf-8')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'ʤ'])


class TestCSVKitDictReader(unittest.TestCase):
    def setUp(self):
        self.f = open('examples/dummy.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csvkit.CSVKitDictReader(self.f)

        self.assertEqual(reader.next(), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })

    def test_reader_alias(self):
        reader = csvkit.DictReader(self.f)

        self.assertEqual(reader.next(), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })

class TestCSVKitDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csvkit.CSVKitDictWriter(self.output, ['a', 'b', 'c'], writeheader=True)
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_writer_alias(self):
        writer = csvkit.DictWriter(self.output, ['a', 'b', 'c'], writeheader=True)
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

