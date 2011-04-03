#!/usr/bin/env python

import datetime
import unittest

from csvkit import typeinference

class TestNormalizeType(unittest.TestCase):
    def test_nulls(self):
        self.assertEqual((None, [None, None, None]), typeinference.normalize_column_type(['', '', '']))

    def test_ints(self): 
        self.assertEqual((int, [1, -87, 418000000, None]), typeinference.normalize_column_type(['1', '-87', '418000000', '']))
    
    def test_floats(self):
        self.assertEqual((float, [1.01, -87.413, 418000000.0, None]), typeinference.normalize_column_type(['1.01', '-87.413', '418000000.0', '']))

    def test_strings(self):
        self.assertEqual((str, ['Chicago Tribune', '435 N Michigan ave', 'Chicago, IL', None]), typeinference.normalize_column_type(['Chicago Tribune', '435 N Michigan ave', 'Chicago, IL', '']))

    def test_ints_floats(self):
        self.assertEqual((float, [1.01, -87, 418000000, None]), typeinference.normalize_column_type(['1.01', '-87', '418000000', '']))

    def test_mixed(self):
        self.assertEqual((str, ['Chicago Tribune', '-87.413', '418000000', None]), typeinference.normalize_column_type(['Chicago Tribune', '-87.413', '418000000', '']))

    def test_booleans(self):
        self.assertEqual((bool, [True, False, True, False, False, True, None]), typeinference.normalize_column_type(['1', 'False', 'TRUE', 'FALSE', '0', 'yes', '']))

    def test_datetimes(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 16, 14, 45), None]), typeinference.normalize_column_type(['Jan 1, 2008 at 4:40 AM', '2010-01-27T03:45:00', '3/1/08 16:14:45', '']))

    def test_dates(self):
        self.assertEqual((datetime.date, [datetime.date(2008, 1, 1), datetime.date(2010, 1, 27), datetime.date(2008, 3, 1), None]), typeinference.normalize_column_type(['Jan 1, 2008', '2010-01-27', '3/1/08', '']))

    def test_times(self):
        self.assertEqual((datetime.time, [datetime.time(4, 40, 0), datetime.time(3, 45, 0), datetime.time(16, 14, 45), None]), typeinference.normalize_column_type(['4:40 AM', '03:45:00', '16:14:45', '']))

    def test_dates_and_times(self):
        self.assertEqual((str, ['Jan 1, 2008', '2010-01-27', '16:14:45', None]), typeinference.normalize_column_type(['Jan 1, 2008', '2010-01-27', '16:14:45', '']))

    def test_datetimes_and_dates(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 0, 0, 0), None]), typeinference.normalize_column_type(['Jan 1, 2008 at 4:40 AM', '2010-01-27T03:45:00', '3/1/08', '']))

    def test_datetimes_and_times(self):
        self.assertEqual((str, ['Jan 1, 2008 at 4:40 AM', '2010-01-27T03:45:00', '16:14:45', None]), typeinference.normalize_column_type(['Jan 1, 2008 at 4:40 AM', '2010-01-27T03:45:00', '16:14:45', '']))


