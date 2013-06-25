#!/usr/bin/env python

import unittest
from csvkit.script import ScriptCSVReader


class TestScript(unittest.TestCase):
    def setUp(self):
        self.tab1 = [
            ['id', 'name', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first'],
            [u'2', u'Chicago Sun-Times', u'only'],
            [u'3', u'Chicago Tribune', u'only'],
            [u'1', u'Chicago Reader', u'second']]


    def test_one_header(self):
        fcr = ScriptCSVReader(iter(self.tab1), scripts=[("Sum", "int(c[1]) + 1")])
        self.assertEqual(['id', 'name', 'i_work_here', 'Sum'], fcr.next())


    def test_one_values(self):
        fcr = list(ScriptCSVReader(iter(self.tab1), scripts=[("Sum", "int(c[1]) + 1")]))
        self.assertEqual([u'1', u'Chicago Reader', u'first', 2], fcr[1])
        self.assertEqual([u'2', u'Chicago Sun-Times', u'only', 3], fcr[2])
        self.assertEqual([u'3', u'Chicago Tribune', u'only', 4], fcr[3])
        self.assertEqual([u'1', u'Chicago Reader', u'second', 2], fcr[4])


    def test_extract_regex(self):
        fcr = list(
            ScriptCSVReader(iter(self.tab1), scripts=[("Re", "re.match('^Chicago (.*)$', ch['name']).group(1)")]))
        self.assertEqual([u'1', u'Chicago Reader', u'first', u'Reader'], fcr[1])
        self.assertEqual([u'2', u'Chicago Sun-Times', u'only', u'Sun-Times'], fcr[2])
        self.assertEqual([u'3', u'Chicago Tribune', u'only', u'Tribune'], fcr[3])
        self.assertEqual([u'1', u'Chicago Reader', u'second', u'Reader'], fcr[4])


