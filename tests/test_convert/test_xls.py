import unittest

import xlrd
from xlrd.xldate import xldate_from_date_tuple as xldate, xldate_from_time_tuple as xltime, xldate_from_datetime_tuple as xldatetime

from csvkit.convert import xls

class TestXLS(unittest.TestCase):
    def test_empty_column(self):
        normal_values = xls.normalize_empty(['', '', ''])
        self.assertEquals(normal_values, [None, None, None])

    def test_text_column(self):
        normal_values = xls.normalize_text([u'This', u'', u'text'])
        self.assertEquals(normal_values, [u'This', None, u'text'])

    def test_numbers_column_integral(self):
        normal_values = xls.normalize_numbers([1.0, 418000000, -817, 0.0, ''])
        self.assertEquals(normal_values, [1, 418000000, -817, 0, None])

    def test_numbers_column_float(self):
        normal_values = xls.normalize_numbers([1.01, 418000000, -817.043, 0.0001, ''])
        self.assertEquals(normal_values, [1.01, 418000000.0, -817.043, 0.0001, None])

    def test_dates_column_dates(self):
        normal_values = xls.normalize_dates([
            xldate((2004, 6, 5), 0),
            xldate((1984, 2, 23), 0),
            xldate((1907, 12, 25), 0),
            ''], 0)
        self.assertEquals(normal_values, ['2004-06-05', '1984-02-23', '1907-12-25', None])

    def test_dates_column_times(self):
        normal_values = xls.normalize_dates([
            xltime((14, 30, 0)),
            xltime((4, 5, 37)),
            xltime((0, 0, 0)),
            ''], 0)
        self.assertEquals(normal_values, ['14:30:00', '04:05:37', '00:00:00', None])

    def test_dates_column_datetimes(self):
        normal_values = xls.normalize_dates([
            xldatetime((2004, 6, 5, 14, 30, 23), 0),
            xldatetime((1984, 2, 23, 0, 0, 0), 0),
            xldatetime((1907, 12, 25, 2, 0, 0), 0),
            ''], 0)
        self.assertEquals(normal_values, ['2004-06-05T14:30:23', '1984-02-23T00:00:00', '1907-12-25T02:00:00', None])

    def test_dates_column_dates_and_times(self):
        self.assertRaises(xls.XLSDataError, xls.normalize_dates, [
            xldate((2004, 6, 5), 0),
            xltime((4, 5, 37)),
            ''], 0)

    def tests_dates_column_dates_and_datetimes(self):
        normal_values = xls.normalize_dates([
            xldate((2004, 6, 5), 0),
            xldatetime((2001, 1, 1, 4, 5, 37), 0),
            ''], 0)
        self.assertEquals(normal_values, ['2004-06-05T00:00:00', '2001-01-01T04:05:37', None])

    def test_dates_column_times_and_datetimes(self):
        self.assertRaises(xls.XLSDataError, xls.normalize_dates, [
            xldatetime((2004, 6, 5, 0, 30, 0), 0),
            xltime((4, 5, 37)),
            ''], 0)

    def test_determine_column_type_single(self):
        column_type = xls.determine_column_type([xlrd.biffh.XL_CELL_NUMBER, xlrd.biffh.XL_CELL_NUMBER, xlrd.biffh.XL_CELL_EMPTY])
        self.assertEquals(column_type, xlrd.biffh.XL_CELL_NUMBER)

    def test_determine_column_type_multiple(self):
        self.assertRaises(xls.XLSDataError, xls.determine_column_type, [xlrd.biffh.XL_CELL_NUMBER, xlrd.biffh.XL_CELL_TEXT, xlrd.biffh.XL_CELL_EMPTY]) 

    def test_determine_column_type_empty(self):
        column_type = xls.determine_column_type([xlrd.biffh.XL_CELL_EMPTY, xlrd.biffh.XL_CELL_EMPTY, xlrd.biffh.XL_CELL_EMPTY])
        self.assertEquals(column_type, xlrd.biffh.XL_CELL_EMPTY) 

    def test_xls(self):
        with open('examples/test.xls', 'r') as f:
            output = xls.xls2csv(f)
        
        with open('examples/testxls_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
