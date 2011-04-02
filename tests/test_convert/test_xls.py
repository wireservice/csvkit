import unittest

import xlrd

from csvkit.convert import xls

class TestXLS(unittest.TestCase):
    def test_empty_column(self):
        normal_values = xls.normalize_empty(['', '', ''])
        self.assertEquals(normal_values, [None, None, None])

    def test_text_column(self):
        normal_values = xls.normalize_text(['This', '', 'text'])
        self.assertEquals(normal_values, ['This', None, 'text'])

    def test_numbers_column_integral(self):
        normal_values = xls.normalize_numbers([1.0, 418000000, -817, 0.0, ''])
        self.assertEquals(normal_values, [1, 418000000, -817, 0, None])

    def test_numbers_column_float(self):
        normal_values = xls.normalize_numbers([1.01, 418000000, -817.043, 0.0001, ''])
        self.assertEquals(normal_values, [1.01, 418000000.0, -817.043, 0.0001, None])

    def test_dates_column_dates(self):
        pass

    def test_dates_column_times(self):
        pass

    def test_dates_column_datetimes(self):
        pass

    def test_dates_column_dates_and_times(self):
        pass

    def tests_dates_column_dates_and_datetimes(self):
        pass

    def test_dates_column_times_and_datetimes(self):
        pass

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
