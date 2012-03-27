#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
import csv
import os
import unittest

from csvkit import unicsv

class TestUnicodeCSVDictReader(unittest.TestCase):
    def setUp(self):
        self.f = open('examples/dummy.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = unicsv.UnicodeCSVDictReader(self.f)

        self.assertEqual(reader.next(), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })

class TestUnicodeCSVDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = unicsv.UnicodeCSVDictWriter(self.output, ['a', 'b', 'c'], writeheader=True)
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\r\n1,2,☃\r\n')

class TestMaxFieldSize(unittest.TestCase):
    def setUp(self):
        self.lim = csv.field_size_limit()

        with open('dummy.csv', 'w') as f:
            f.write('a' * 10)
            f.close()

    def tearDown(self):
        # Resetting limit to avoid failure in other tests.
        csv.field_size_limit(self.lim)
        os.system('rm dummy.csv')

    def test_maxfieldsize(self):
        # Testing --maxfieldsize for failure. Creating data using str * int.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=9)
            try:
                c.next()
            except unicsv.FieldSizeLimitError:
                pass
            else:
                raise AssertionError('Expected unicsv.FieldSizeLimitError')

        # Now testing higher --maxfieldsize.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=11)
            self.assertEqual(['a' * 10], c.next())

