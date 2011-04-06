import unittest

from csvkit.convert import utils

class TestGuessFormat(unittest.TestCase):
    def test_fixed(self):
        format = utils.guess_format('testdata')
        self.assertEqual(format, 'fixed')

    def test_xls(self):
        format = utils.guess_format('testdata.xls')
        self.assertEqual(format, 'xls')
    
    def test_csv(self):
        self.assertEqual('csv', utils.guess_format('testdata.csv'))
