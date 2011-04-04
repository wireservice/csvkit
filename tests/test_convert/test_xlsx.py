import datetime
import unittest

from csvkit.convert import xlsx

class TestXLSX(unittest.TestCase):
    def test_normalize_nulls(self):
        normal_values = xlsx.normalize_column_type(['', '', ''])
        self.assertEquals(normal_values, (None, [None, None, None]))

    def test_normalize_strings(self):
        normal_values = xlsx.normalize_column_type(['This', '', 'text'])
        self.assertEquals(normal_values, (str, ['This', None, 'text']))

    def test_normalize_integers(self):
        normal_values = xlsx.normalize_column_type([1.0, 418000000, -817, 0.0, ''])
        self.assertEquals(normal_values, (int, [1, 418000000, -817, 0, None]))

    def test_normalize_floats(self):
        normal_values = xlsx.normalize_column_type([1.01, 418000000, -817.043, 0.0001, ''])
        self.assertEquals(normal_values, (float, [1.01, 418000000.0, -817.043, 0.0001, None]))
    
    def test_normalize_booleans(self):
        # TKTK
        pass
    
    def test_dates_column_dates(self):
        normal_values = xlsx.normalize_column_type([datetime.date(2004, 6, 5), datetime.date(1984, 2, 23), datetime.date(1907, 12, 25), ''])
        self.assertEquals(normal_values, (datetime.date, [datetime.date(2004, 6, 5), datetime.date(1984, 2, 23), datetime.date(1907, 12, 25), None]))
    
    def test_dates_column_times(self):
        normal_values = xlsx.normalize_column_type([datetime.time(14, 30, 0), datetime.time(4, 5, 37), datetime.time(0, 0, 0), ''])
        self.assertEquals(normal_values, (datetime.time, [datetime.time(14, 30, 0), datetime.time(4, 5, 37), datetime.time(0, 0, 0), None]))

    def test_dates_column_datetimes(self):
        normal_values = xlsx.normalize_column_type([datetime.datetime(2004, 6, 5, 14, 30, 23), datetime.datetime(1984, 2, 23, 0, 0, 0), datetime.datetime(1907, 12, 25, 2, 0, 0), ''])
        self.assertEquals(normal_values, (datetime.datetime, [datetime.datetime(2004, 6, 5, 14, 30, 23), datetime.datetime(1984, 2, 23, 0, 0, 0), datetime.datetime(1907, 12, 25, 2, 0, 0), None]))
    
    def test_dates_column_dates_and_times(self):
        self.assertRaises(xlsx.XLSXDataError, xlsx.normalize_column_type, [datetime.date(2004, 6, 5), datetime.time(4, 5, 37), ''])

    def tests_dates_column_dates_and_datetimes(self):
        normal_values = xlsx.normalize_column_type([datetime.date(2004, 6, 5), datetime.datetime(2001, 1, 1, 4, 5, 37), ''])
        self.assertEquals(normal_values, (datetime.datetime, [datetime.date(2004, 6, 5), datetime.datetime(2001, 1, 1, 4, 5, 37), None]))

    def test_dates_column_times_and_datetimes(self):
        self.assertRaises(xlsx.XLSXDataError, xlsx.normalize_column_type, [datetime.datetime(2004, 6, 5, 0, 30, 0), datetime.time(4, 5, 37)])
    
    def test_xlsx(self):
        with open('examples/test.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f)
        
        with open('examples/testxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

