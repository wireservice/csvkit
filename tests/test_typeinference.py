#!/usr/bin/env python

from csvkit import typeinference

import unittest

class TestSimpleInference(unittest.TestCase):
    def test_ints(self): 
        self.assertEqual([1, -87, 418000000], typeinference.infer_simple_type(['1', '-87', '418000000']))
    
    def test_floats(self):
        self.assertEqual([1.01, -87.413, 418000000.0], typeinference.infer_simple_type(['1.01', '-87.413', '418000000.0']))

    def test_strings(self):
        self.assertEqual(['Chicago Tribune', '435 N Michigan ave', 'Chicago, IL'], typeinference.infer_simple_type(['Chicago Tribune', '435 N Michigan ave', 'Chicago, IL']))

    def test_ints_floats(self):
        self.assertEqual([1.01, -87, 418000000], typeinference.infer_simple_type(['1.01', '-87', '418000000']))

    def test_mixed(self):
        self.assertEqual(['Chicago Tribune', '-87.413', '418000000'], typeinference.infer_simple_type(['Chicago Tribune', '-87.413', '418000000']))

