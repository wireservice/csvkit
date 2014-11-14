#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import csvkit

@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestCSVKitReader(unittest.TestCase):
    def test_utf8(self):
        with open('examples/test_utf8.csv', encoding='utf-8') as f:
            reader = csvkit.CSVKitReader(f)
            self.assertEqual(next(reader), ['a', 'b', 'c'])
            self.assertEqual(next(reader), ['1', '2', '3'])
            self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_reader_alias(self):
        with open('examples/test_utf8.csv', encoding='utf-8') as f:
            reader = csvkit.reader(f)
            self.assertEqual(next(reader), ['a', 'b', 'c'])
            self.assertEqual(next(reader), ['1', '2', '3'])
            self.assertEqual(next(reader), ['4', '5', u'ʤ'])


@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestCSVKitWriter(unittest.TestCase):
    def test_utf8(self):
        output = six.StringIO()
        writer = csvkit.CSVKitWriter(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csvkit.CSVKitReader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_writer_alias(self):
        output = six.StringIO()
        writer = csvkit.writer(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csvkit.reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])


@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestCSVKitDictReader(unittest.TestCase):
    def setUp(self):
        self.f = open('examples/dummy.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csvkit.CSVKitDictReader(self.f)

        self.assertEqual(next(reader), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })

    def test_reader_alias(self):
        reader = csvkit.DictReader(self.f)

        self.assertEqual(next(reader), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })


@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestCSVKitDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = six.StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csvkit.CSVKitDictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_writer_alias(self):
        writer = csvkit.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

