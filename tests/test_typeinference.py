#!/usr/bin/env python

import datetime
from types import NoneType
import unittest

from csvkit import typeinference

from csvkit.exceptions import InvalidValueForTypeException, InvalidValueForTypeListException

class TestNormalizeType(unittest.TestCase):
    def test_nulls(self):
        self.assertEqual((NoneType, [None, None, None, None, None, None]), typeinference.normalize_column_type([u'n/a', u'NA', u'.', u'null', u'none', u'']))

    def test_nulls_coerce(self):
        self.assertEqual((NoneType, [None, None, None, None, None, None]), typeinference.normalize_column_type([u'n/a', u'NA', u'.', u'null', u'none', u''], normal_type=NoneType))

    def test_nulls_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'n/a', u'NA', u'.', u'1.7', u'none', u''], normal_type=NoneType)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, '1.7')
        self.assertEqual(e.exception.normal_type, NoneType)

    def test_ints(self): 
        self.assertEqual((int, [1, -87, 418000000, None]), typeinference.normalize_column_type([u'1', u'-87', u'418000000', u'']))

    def test_ints_coerce(self): 
        self.assertEqual((int, [1, -87, 418000000, None]), typeinference.normalize_column_type([u'1', u'-87', u'418000000', u''], normal_type=int))

    def test_ints_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'1', u'-87', u'418000000', u'', u'TRUE'], normal_type=int)

        self.assertEqual(e.exception.index, 4)
        self.assertEqual(e.exception.value, 'TRUE')
        self.assertEqual(e.exception.normal_type, int)

    def test_padded_ints(self):
        self.assertEqual((unicode, [u'0001', u'0997', u'8.7', None]), typeinference.normalize_column_type([u'0001', u'0997', u'8.7', u'']))

    def test_padded_ints_coerce(self):
        self.assertEqual((unicode, [u'0001', u'0997', u'8.7', None]), typeinference.normalize_column_type([u'0001', u'0997', u'8.7', u''], normal_type='unicode'))

    def test_padded_ints_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'0001', u'0997', u'8.7', u''], normal_type=int)

        self.assertEqual(e.exception.index, 0)
        self.assertEqual(e.exception.value, '0001')
        self.assertEqual(e.exception.normal_type, int)

    def test_comma_ints(self):
        self.assertEqual((int, [1, -87, 418000000, None]), typeinference.normalize_column_type([u'1', u'-87', u'418,000,000', u'']))
    
    def test_floats(self):
        self.assertEqual((float, [1.01, -87.413, 418000000.0, None]), typeinference.normalize_column_type([u'1.01', u'-87.413', u'418000000.0', u'']))

    def test_floats_coerce(self):
        self.assertEqual((float, [1.01, -87.413, 418000000.0, None]), typeinference.normalize_column_type([u'1.01', u'-87.413', u'418000000.0', u''], normal_type=float))

    def test_floats_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'1', u'-87.413', u'418000000.0', u'Hello, world!'], normal_type=float)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, 'Hello, world!')
        self.assertEqual(e.exception.normal_type, float)
        
    def test_comma_floats(self):
        self.assertEqual((float, [1.01, -87.413, 418000000.0, None]), typeinference.normalize_column_type([u'1.01', u'-87.413', u'418,000,000.0', u'']))

    def test_strings(self):
        self.assertEqual((unicode, [u'Chicago Tribune', u'435 N Michigan ave', u'Chicago, IL', None]), typeinference.normalize_column_type([u'Chicago Tribune', u'435 N Michigan ave', u'Chicago, IL', u'']))

    def test_strings_coerce(self):
        self.assertEqual((unicode, [u'Chicago Tribune', u'435 N Michigan ave', u'Chicago, IL', None]), typeinference.normalize_column_type([u'Chicago Tribune', u'435 N Michigan ave', u'Chicago, IL', u''], normal_type=unicode))

    def test_ints_floats(self):
        self.assertEqual((float, [1.01, -87, 418000000, None]), typeinference.normalize_column_type([u'1.01', u'-87', u'418000000', u'']))

    def test_mixed(self):
        self.assertEqual((unicode, [u'Chicago Tribune', u'-87.413', u'418000000', None]), typeinference.normalize_column_type([u'Chicago Tribune', u'-87.413', u'418000000', u'']))

    def test_booleans(self):
        self.assertEqual((bool, [False, True, False, True, None]), typeinference.normalize_column_type([u'False', u'TRUE', u'FALSE', u'yes', u'']))

    def test_booleans_coerce(self):
        self.assertEqual((bool, [False, True, False, True, None]), typeinference.normalize_column_type([u'False', u'TRUE', u'FALSE', u'yes', u''], normal_type=bool))

    def test_booleans_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'False', u'TRUE', u'FALSE', u'17', u''], normal_type=bool)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, '17')
        self.assertEqual(e.exception.normal_type, bool)

    def test_datetimes(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 16, 14, 45), None]), typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', u'']))

    def test_datetimes_coerce(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 16, 14, 45), None]), typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', u''], normal_type=datetime.datetime))

    def test_datetimes_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', u'4:45 AM'], normal_type=datetime.datetime)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, '4:45 AM')
        self.assertEqual(e.exception.normal_type, datetime.datetime)

    def test_dates(self):
        self.assertEqual((datetime.date, [datetime.date(2008, 1, 1), datetime.date(2010, 1, 27), datetime.date(2008, 3, 1), None]), typeinference.normalize_column_type([u'Jan 1, 2008', u'2010-01-27', u'3/1/08', u'']))

    def test_dates_coerce(self):
        self.assertEqual((datetime.date, [datetime.date(2008, 1, 1), datetime.date(2010, 1, 27), datetime.date(2008, 3, 1), None]), typeinference.normalize_column_type([u'Jan 1, 2008', u'2010-01-27', u'3/1/08', u''], normal_type=datetime.date))

    def test_dates_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08 16:14:45', u'4:45 AM'], normal_type=datetime.datetime)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, '4:45 AM')
        self.assertEqual(e.exception.normal_type, datetime.datetime)

    def test_times(self):
        self.assertEqual((datetime.time, [datetime.time(4, 40, 0), datetime.time(3, 45, 0), datetime.time(16, 14, 45), None]), typeinference.normalize_column_type([u'4:40 AM', u'03:45:00', u'16:14:45', u'']))

    def test_times_coerce(self):
        self.assertEqual((datetime.time, [datetime.time(4, 40, 0), datetime.time(3, 45, 0), datetime.time(16, 14, 45), None]), typeinference.normalize_column_type([u'4:40 AM', u'03:45:00', u'16:14:45', u''], normal_type=datetime.time))

    def test_times_coerce_fail(self):
        with self.assertRaises(InvalidValueForTypeException) as e:
            typeinference.normalize_column_type([u'4:40 AM', u'03:45:00', u'16:14:45', u'1,000,000'], normal_type=datetime.time)

        self.assertEqual(e.exception.index, 3)
        self.assertEqual(e.exception.value, '1,000,000')
        self.assertEqual(e.exception.normal_type, datetime.time)

    def test_dates_and_times(self):
        self.assertEqual((unicode, [u'Jan 1, 2008', u'2010-01-27', u'16:14:45', None]), typeinference.normalize_column_type([u'Jan 1, 2008', u'2010-01-27', u'16:14:45', u'']))

    def test_datetimes_and_dates(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 0, 0, 0), None]), typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08', u'']))

    def test_datetimes_and_dates_coerce(self):
        self.assertEqual((datetime.datetime, [datetime.datetime(2008, 1, 1, 4, 40, 0), datetime.datetime(2010, 1, 27, 3, 45, 0), datetime.datetime(2008, 3, 1, 0, 0, 0), None]), typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'3/1/08', u''], normal_type=datetime.datetime))

    def test_datetimes_and_times(self):
        self.assertEqual((unicode, [u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'16:14:45', None]), typeinference.normalize_column_type([u'Jan 1, 2008 at 4:40 AM', u'2010-01-27T03:45:00', u'16:14:45', u'']))

    def test_normalize_table(self):
        expected_types = [unicode, int, float, NoneType]
        data = [
            [u'a', u'1', u'2.1', u''],
            [u'b', u'5', u'4.1'],
            [u'c', u'100', u'100.9999', u''],
            [u'd', u'2', u'5.3', u'']
        ]
        types, columns = typeinference.normalize_table(data)

        self.assertEqual(4, len(types))
        self.assertEqual(4, len(columns))

        for i, tup in enumerate(zip(columns, types, expected_types)):
            c, t, et = tup
            self.assertEqual(et, t)
            for row, normalized in zip(data, c):
                if t is NoneType:
                    self.assertTrue(normalized is None)
                else:
                    self.assertEqual(t(row[i]), normalized)

    def test_normalize_table_known_types(self):
        normal_types = [unicode, int, float, NoneType]
        data = [
            [u'a', u'1', u'2.1', u''],
            [u'b', u'5', u'4.1'],
            [u'c', u'100', u'100.9999', u''],
            [u'd', u'2', u'5.3', u'']
        ]
        types, columns = typeinference.normalize_table(data, normal_types)

        self.assertEqual(4, len(types))
        self.assertEqual(4, len(columns))

        for i, tup in enumerate(zip(columns, types, normal_types)):
            c, t, et = tup
            self.assertEqual(et, t)
            for row, normalized in zip(data, c):
                if t is NoneType:
                    self.assertTrue(normalized is None)
                else:
                    self.assertEqual(t(row[i]), normalized)

    def test_normalize_table_known_types_invalid(self):
        normal_types = [bool, int, int, NoneType]
        data = [
            [u'a', u'1', u'2.1', u''],
            [u'b', u'5', u'4.1'],
            [u'c', u'100', u'100.9999', u''],
            [u'd', u'2', u'5.3', u'']
        ]
        
        try:
            typeinference.normalize_table(data, normal_types, accumulate_errors=True)
            self.assertEqual(True, False)
        except InvalidValueForTypeListException, e:
            self.assertEqual(len(e.errors), 2)
            self.assertEqual(e.errors[0].index, 0)
            self.assertEqual(e.errors[0].value, 'a')
            self.assertEqual(e.errors[0].normal_type, bool)
            self.assertEqual(e.errors[2].index, 0)
            self.assertEqual(e.errors[2].value, '2.1')
            self.assertEqual(e.errors[2].normal_type, int)

    def test_can_be_bool(self):
        for val in ['yes', 'y', 'true', 't', 'True', 'TRUE', 'YES', 'no', 'n', 'false', 'f', 'NO', 'False']:
            self.assertTrue(typeinference.can_be_bool(val), val + " should be a valid boolean string")
        for val in ['1', '0', 'bob', 'nyet', 'si']:
            self.assertFalse(typeinference.can_be_bool(val), val + " should not be a valid boolean string")

    def test_can_be_int(self):
        for val in ['1', '100', '1,000', '5215', '5,235,125']:
            self.assertTrue(typeinference.can_be_int(val), val + " should be a valid int string")
        for val in ['bob', 'nyet', '01010', '(312) 555-1212', 'palindrome', '3.14', '1.21']:
            self.assertFalse(typeinference.can_be_int(val), val + " should not be a valid int string")            
            
    def test_can_be_float(self):
        for val in ['1', '100', '1,000', '5215', '5,235,125', '1.0', '3.14', '1.21', '0.19', '01010']:
            self.assertTrue(typeinference.can_be_float(val), val + " should be a valid float string")
        for val in ['bob', 'nyet', '(312) 555-1212', 'palindrome']:
            self.assertFalse(typeinference.can_be_float(val), val + " should not be a valid float string")            

    def test_can_be_date(self):
        for val in ['12/25/2011', 'July 6, 1971', '1941-12-07']:
            self.assertTrue(typeinference.can_be_date(val), val + " should be a valid date string")            
        for val in ['12/25/2011 5:00 pm', '1941-12-07 4:32am', '5:00 pm', '12am', '4:32am']:
            self.assertFalse(typeinference.can_be_date(val), val + " should not be a valid date string")            
    
    def test_can_be_time(self):
        for val in ['5:00 pm', '12am', '4:32am']:
            self.assertTrue(typeinference.can_be_time(val), val + " should be a valid time string")            
        for val in ['12/25/2011 5:00 pm', 'July 6, 1971 12am', '1941-12-07 4:32am', '12/25/2011', 'July 6, 1971', '1941-12-07']:
            self.assertFalse(typeinference.can_be_time(val), val + " should be a valid time string")            

    def test_can_be_datetime(self):
        for val in ['12/25/2011 5:00 pm', 'July 6, 1971 12:01am', '1941-12-07 4:32am', '1941-12-07', '12/25/2011', 'July 6, 1971']:
            self.assertTrue(typeinference.can_be_datetime(val), val + " should be a valid datetime string")            

        for val in ['5:00 pm', '12am', '4:32am']:
            self.assertFalse(typeinference.can_be_datetime(val), val + " should not be a valid datetime string")            
    
    def test_assess_row(self):
        rows = [
            ['5', '1',   'bob',          'true',  '1/1/2001',   '1/1/2002 5:00pm'],
            ['4', '2.0', 'more strings', 'false', '12-31-2009', '1/1/2002'],
            ['4', '',    'more strings', '',      '4/1/2010',   ''],
        ]
        
        limits = typeinference.assess_row(rows[0])
        self.assert_assessments(limits[0], (int, float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[1], (int, float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[2], (unicode,))
        self.assert_assessments(limits[3], (bool, unicode))
        self.assert_assessments(limits[4], (datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[5], (datetime.datetime, unicode))

        limits = typeinference.assess_row(rows[1], limits)
        self.assert_assessments(limits[0], (int, float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[1], (float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[2], (unicode,))
        self.assert_assessments(limits[3], (bool, unicode))
        self.assert_assessments(limits[4], (datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[5], (datetime.datetime, unicode))

        limits = typeinference.assess_row(rows[2], limits)
        self.assert_assessments(limits[0], (int, float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[1], (float, datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[2], (unicode,))
        self.assert_assessments(limits[3], (bool, unicode))
        self.assert_assessments(limits[4], (datetime.datetime, datetime.date, unicode))
        self.assert_assessments(limits[5], (datetime.datetime, unicode))

        limits = typeinference.reduce_assessment(limits)
        self.assertEqual(int, limits[0])
        self.assertEqual(float, limits[1])
        self.assertEqual(unicode, limits[2])
        self.assertEqual(bool, limits[3])
        self.assertEqual(datetime.date, limits[4])
        self.assertEqual(datetime.datetime, limits[5])
        
    def assert_assessments(self, assessment, allowed):
        self.assertEqual(len(assessment), len(allowed), "len of assessment should be %i, not %i %s" % (len(allowed), len(assessment), assessment))

        for item in allowed:
            self.assertTrue(item in assessment, 'expected %s' % item)
        
    def test_reduce_assessment(self):
        reducify = typeinference.reduce_assessment
        self.assertEqual(reducify([set([unicode])]), [unicode])
        self.assertEqual(reducify([set([unicode, int])]), [int])
        self.assertEqual(reducify([set([unicode, datetime.datetime, datetime.date])]), [datetime.date])
        self.assertEqual(reducify([set([unicode, datetime.datetime, datetime.time])]), [unicode])
        self.assertEqual(reducify([set([unicode, float, int])]), [int])
        self.assertEqual(reducify([set([unicode, bool, int])]), [bool])
        self.assertEqual(reducify([set([unicode, bool, int, float])]), [bool])
        
        
