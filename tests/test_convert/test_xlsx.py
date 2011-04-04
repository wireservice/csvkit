import datetime
import unittest

from csvkit.convert import xlsx

class TestXLSX(unittest.TestCase):
    def test_normalize_nulls(self):
        normal_values = xlsx.normalize_nulls(['', '', ''])
        self.assertEquals(normal_values, [None, None, None])

    def test_normalize_strings(self):
        normal_values = xlsx.normalize_strings(['This', '', 'text'])
        self.assertEquals(normal_values, ['This', None, 'text'])

    def test_normalize_integers(self):
        normal_values = xlsx.normalize_numerics([1.0, 418000000, -817, 0.0, ''])
        self.assertEquals(normal_values, [1, 418000000, -817, 0, None])

    def test_normalize_floats(self):
        normal_values = xlsx.normalize_numerics([1.01, 418000000, -817.043, 0.0001, ''])
        self.assertEquals(normal_values, [1.01, 418000000.0, -817.043, 0.0001, None])
    
    def test_normalize_booleans(self):
        # TKTK
        pass
    
    def test_dates_column_dates(self):
        normal_values = xlsx.normalize_dates([datetime.date(2004, 6, 5), datetime.date(1984, 2, 23), datetime.date(1907, 12, 25), ''])
        self.assertEquals(normal_values, ['2004-06-05', '1984-02-23', '1907-12-25', None])
    
    def test_dates_column_times(self):
        normal_values = xlsx.normalize_dates([datetime.time(14, 30, 0), datetime.time(4, 5, 37), datetime.time(0, 0, 0), ''])
        self.assertEquals(normal_values, ['14:30:00', '04:05:37', '00:00:00', None])

    def test_dates_column_datetimes(self):
        normal_values = xlsx.normalize_dates([datetime.datetime(2004, 6, 5, 14, 30, 23), datetime.datetime(1984, 2, 23, 0, 0, 0), datetime.datetime(1907, 12, 25, 2, 0, 0), ''])
        self.assertEquals(normal_values, ['2004-06-05T14:30:23', '1984-02-23T00:00:00', '1907-12-25T02:00:00', None])
    
    def test_dates_column_dates_and_times(self):
        self.assertRaises(xlsx.XLSXDataError, xlsx.normalize_dates, [datetime.date(2004, 6, 5), datetime.time(4, 5, 37), ''])

    def tests_dates_column_dates_and_datetimes(self):
        normal_values = xlsx.normalize_dates([datetime.date(2004, 6, 5), datetime.datetime(2001, 1, 1, 4, 5, 37), ''])
        self.assertEquals(normal_values, ['2004-06-05T00:00:00', '2001-01-01T04:05:37', None])

    def test_dates_column_times_and_datetimes(self):
        self.assertRaises(xlsx.XLSXDataError, xlsx.normalize_dates, [datetime.datetime(2004, 6, 5, 0, 30, 0), datetime.time(4, 5, 37)])
    
    def test_xlsx(self):
        with open('examples/test.xlsx', 'rb') as f:
            output = xlsx.xlsx2csv(f)
        
        with open('examples/testxlsx_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

