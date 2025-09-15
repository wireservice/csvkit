#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
testtimeparse.py
(c) Will Roberts <wildwilhelm@gmail.com>  1 February, 2014

Unit tests for the `timeparse` module.
'''

from __future__ import absolute_import
import doctest
import re
from .. import timeparse
import unittest

class TestTimeparse(unittest.TestCase):
    '''
    Unit tests for the `timeparse` module.
    '''

    def setUp(self):
        '''Setup function.'''
        pass

    def test_mins(self):
        '''Test parsing minutes.'''
        self.assertEqual(re.match(timeparse.MINS, '32min').groupdict(),
                         {'mins': '32'})
        self.assertEqual(re.match(timeparse.MINS, '32mins').groupdict(),
                         {'mins': '32'})
        self.assertEqual(re.match(timeparse.MINS, '32minute').groupdict(),
                         {'mins': '32'})
        self.assertEqual(re.match(timeparse.MINS, '32minutes').groupdict(),
                         {'mins': '32'})
        self.assertEqual(re.match(timeparse.MINS, '32mins').groupdict(),
                         {'mins': '32'})
        self.assertEqual(re.match(timeparse.MINS, '32min').groupdict(),
                         {'mins': '32'})

    def test_hrs(self):
        '''Test parsing hours.'''
        self.assertEqual(re.match(timeparse.HOURS, '32h').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32hr').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32hrs').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32hour').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32hours').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32 hours').groupdict(),
                         {'hours': '32'})
        self.assertEqual(re.match(timeparse.HOURS, '32 h').groupdict(),
                         {'hours': '32'})

    def test_time(self):
        '''Test parsing time expression.'''
        self.assertGreater(
            set(re.match(timeparse.TIMEFORMATS[0] + r'\s*$',
                         '16h32m64s  ').groupdict().items()),
            set([('hours', '16'), ('mins', '32'), ('secs', '64')]))

    def test_timeparse_multipliers(self):
        '''Test parsing time unit multipliers.'''
        self.assertEqual(timeparse.timeparse('32 min'),
                         1920)
        self.assertEqual(timeparse.timeparse('1 min'),
                         60)
        self.assertEqual(timeparse.timeparse('1 hours'),
                         3600)
        self.assertEqual(timeparse.timeparse('1 day'),
                         86400)
        self.assertEqual(timeparse.timeparse('1 sec'),
                         1)

    def test_timeparse_signs(self):
        '''Test parsing time signs.'''
        self.assertEqual(timeparse.timeparse('+32 m 1 s'), 1921)
        self.assertEqual(timeparse.timeparse('+ 32 m 1 s'), 1921)
        self.assertEqual(timeparse.timeparse('-32 m 1 s'), -1921)
        self.assertEqual(timeparse.timeparse('- 32 m 1 s'), -1921)
        self.assertIsNone(timeparse.timeparse('32 m - 1 s'))
        self.assertIsNone(timeparse.timeparse('32 m + 1 s'))

    def test_timeparse_1(self):
        '''timeparse test case 1.'''
        self.assertEqual(timeparse.timeparse('32m'), 1920)
        self.assertEqual(timeparse.timeparse('+32m'), 1920)
        self.assertEqual(timeparse.timeparse('-32m'), -1920)

    def test_timeparse_2(self):
        '''timeparse test case 2.'''
        self.assertEqual(timeparse.timeparse('2h32m'), 9120)
        self.assertEqual(timeparse.timeparse('+2h32m'), 9120)
        self.assertEqual(timeparse.timeparse('-2h32m'), -9120)

    def test_timeparse_3(self):
        '''timeparse test case 3.'''
        self.assertEqual(timeparse.timeparse('3d2h32m'), 268320)
        self.assertEqual(timeparse.timeparse('+3d2h32m'), 268320)
        self.assertEqual(timeparse.timeparse('-3d2h32m'), -268320)

    def test_timeparse_4(self):
        '''timeparse test case 4.'''
        self.assertEqual(timeparse.timeparse('1w3d2h32m'), 873120)
        self.assertEqual(timeparse.timeparse('+1w3d2h32m'), 873120)
        self.assertEqual(timeparse.timeparse('-1w3d2h32m'), -873120)

    def test_timeparse_5(self):
        '''timeparse test case 5.'''
        self.assertEqual(timeparse.timeparse('1w 3d 2h 32m'), 873120)
        self.assertEqual(timeparse.timeparse('+1w 3d 2h 32m'), 873120)
        self.assertEqual(timeparse.timeparse('-1w 3d 2h 32m'), -873120)

    def test_timeparse_6(self):
        '''timeparse test case 6.'''
        self.assertEqual(timeparse.timeparse('1 w 3 d 2 h 32 m'), 873120)
        self.assertEqual(timeparse.timeparse('+1 w 3 d 2 h 32 m'), 873120)
        self.assertEqual(timeparse.timeparse('-1 w 3 d 2 h 32 m'), -873120)

    def test_timeparse_7(self):
        '''timeparse test case 7.'''
        self.assertEqual(timeparse.timeparse('4:13'), 253)
        self.assertEqual(timeparse.timeparse('+4:13'), 253)
        self.assertEqual(timeparse.timeparse('-4:13'), -253)

    def test_timeparse_bare_seconds(self):
        '''timeparse test bare seconds, without minutes.'''
        self.assertEqual(timeparse.timeparse(':13'), 13)
        self.assertEqual(timeparse.timeparse('+:13'), 13)
        self.assertEqual(timeparse.timeparse('-:13'), -13)

    def test_timeparse_8(self):
        '''timeparse test case 8.'''
        self.assertEqual(timeparse.timeparse('4:13:02'), 15182)
        self.assertEqual(timeparse.timeparse('+4:13:02'), 15182)
        self.assertEqual(timeparse.timeparse('-4:13:02'), -15182)

    def test_timeparse_9(self):
        '''timeparse test case 9.'''
        self.assertAlmostEqual(timeparse.timeparse('4:13:02.266'), 15182.266)
        self.assertAlmostEqual(timeparse.timeparse('+4:13:02.266'), 15182.266)
        self.assertAlmostEqual(timeparse.timeparse('-4:13:02.266'), -15182.266)

    def test_timeparse_10(self):
        '''timeparse test case 10.'''
        self.assertAlmostEqual(timeparse.timeparse('2:04:13:02.266'),
                               187982.266)
        self.assertAlmostEqual(timeparse.timeparse('+2:04:13:02.266'),
                               187982.266)
        self.assertAlmostEqual(timeparse.timeparse('-2:04:13:02.266'),
                               -187982.266)

    def test_timeparse_granularity_1(self):
        '''Check that minute-level granularity applies correctly.'''
        self.assertEqual(timeparse.timeparse('4:32', granularity='minutes'), 272*60)
        self.assertEqual(timeparse.timeparse('+4:32', granularity='minutes'), 272*60)
        self.assertEqual(timeparse.timeparse('-4:32', granularity='minutes'), -272*60)

    def test_timeparse_granularity_2(self):
        '''Check that minute-level granularity does not apply inappropriately.'''
        self.assertEqual(timeparse.timeparse('4:32:02', granularity='minutes'), 272*60+2)
        self.assertEqual(timeparse.timeparse('+4:32:02', granularity='minutes'), 272*60+2)
        self.assertEqual(timeparse.timeparse('-4:32:02', granularity='minutes'), -(272*60+2))

    def test_timeparse_granularity_3(self):
        '''Check that minute-level granularity does not apply inappropriately.'''
        self.assertAlmostEqual(timeparse.timeparse('7:02.223', granularity='minutes'), 7*60 + 2.223)
        self.assertAlmostEqual(timeparse.timeparse('+7:02.223', granularity='minutes'), 7*60 + 2.223)
        self.assertAlmostEqual(timeparse.timeparse('-7:02.223', granularity='minutes'), -(7*60 + 2.223))

    def test_timeparse_granularity_4(self):
        '''Check that minute-level granularity does not apply inappropriately.'''
        self.assertEqual(timeparse.timeparse('0:02', granularity='seconds'), 2)
        self.assertEqual(timeparse.timeparse('+0:02', granularity='seconds'), 2)
        self.assertEqual(timeparse.timeparse('-0:02', granularity='seconds'), -2)

    def test_timeparse_11(self):
        '''timeparse test case 11.'''
        # uptime format
        self.assertEqual(timeparse.timeparse('2 days,  4:13:02'), 187982)
        self.assertEqual(timeparse.timeparse('+2 days,  4:13:02'), 187982)
        self.assertEqual(timeparse.timeparse('-2 days,  4:13:02'), -187982)

    def test_timeparse_12(self):
        '''timeparse test case 12.'''
        self.assertAlmostEqual(timeparse.timeparse('2 days,  4:13:02.266'),
                               187982.266)
        self.assertAlmostEqual(timeparse.timeparse('+2 days,  4:13:02.266'),
                               187982.266)
        self.assertAlmostEqual(timeparse.timeparse('-2 days,  4:13:02.266'),
                               -187982.266)

    def test_timeparse_13(self):
        '''timeparse test case 13.'''
        self.assertEqual(timeparse.timeparse('5hr34m56s'), 20096)
        self.assertEqual(timeparse.timeparse('+5hr34m56s'), 20096)
        self.assertEqual(timeparse.timeparse('-5hr34m56s'), -20096)

    def test_timeparse_14(self):
        '''timeparse test case 14.'''
        self.assertEqual(timeparse.timeparse('5 hours, 34 minutes, 56 seconds'),
                         20096)
        self.assertEqual(timeparse.timeparse('+5 hours, 34 minutes, 56 seconds'),
                         20096)
        self.assertEqual(timeparse.timeparse('-5 hours, 34 minutes, 56 seconds'),
                         -20096)

    def test_timeparse_15(self):
        '''timeparse test case 15.'''
        self.assertEqual(timeparse.timeparse('5 hrs, 34 mins, 56 secs'), 20096)
        self.assertEqual(timeparse.timeparse('+5 hrs, 34 mins, 56 secs'), 20096)
        self.assertEqual(timeparse.timeparse('-5 hrs, 34 mins, 56 secs'), -20096)

    def test_timeparse_16(self):
        '''timeparse test case 16.'''
        self.assertEqual(
            timeparse.timeparse('2 days, 5 hours, 34 minutes, 56 seconds'),
            192896)
        self.assertEqual(
            timeparse.timeparse('+2 days, 5 hours, 34 minutes, 56 seconds'),
            192896)
        self.assertEqual(
            timeparse.timeparse('-2 days, 5 hours, 34 minutes, 56 seconds'),
            -192896)

    def test_timeparse_16b(self):
        '''timeparse test case 16b.'''
        self.assertAlmostEqual(timeparse.timeparse('1.75 s'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('+1.75 s'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('-1.75 s'), -1.75)

    def test_timeparse_16c(self):
        '''timeparse test case 16c.'''
        self.assertAlmostEqual(timeparse.timeparse('1.75 sec'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('+1.75 sec'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('-1.75 sec'), -1.75)

    def test_timeparse_16d(self):
        '''timeparse test case 16d.'''
        self.assertAlmostEqual(timeparse.timeparse('1.75 secs'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('+1.75 secs'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('-1.75 secs'), -1.75)

    def test_timeparse_16e(self):
        '''timeparse test case 16e.'''
        self.assertAlmostEqual(timeparse.timeparse('1.75 second'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('+1.75 second'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('-1.75 second'), -1.75)

    def test_timeparse_16f(self):
        '''timeparse test case 16f.'''
        self.assertAlmostEqual(timeparse.timeparse('1.75 seconds'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('+1.75 seconds'), 1.75)
        self.assertAlmostEqual(timeparse.timeparse('-1.75 seconds'), -1.75)

    def test_timeparse_17(self):
        '''timeparse test case 17.'''
        self.assertEqual(timeparse.timeparse('1.2 m'), 72)
        self.assertEqual(timeparse.timeparse('+1.2 m'), 72)
        self.assertEqual(timeparse.timeparse('-1.2 m'), -72)

    def test_timeparse_18(self):
        '''timeparse test case 18.'''
        self.assertEqual(timeparse.timeparse('1.2 min'), 72)
        self.assertEqual(timeparse.timeparse('+1.2 min'), 72)
        self.assertEqual(timeparse.timeparse('-1.2 min'), -72)

    def test_timeparse_19(self):
        '''timeparse test case 19.'''
        self.assertEqual(timeparse.timeparse('1.2 mins'), 72)
        self.assertEqual(timeparse.timeparse('+1.2 mins'), 72)
        self.assertEqual(timeparse.timeparse('-1.2 mins'), -72)

    def test_timeparse_20(self):
        '''timeparse test case 20.'''
        self.assertEqual(timeparse.timeparse('1.2 minute'), 72)
        self.assertEqual(timeparse.timeparse('+1.2 minute'), 72)
        self.assertEqual(timeparse.timeparse('-1.2 minute'), -72)

    def test_timeparse_21(self):
        '''timeparse test case 21.'''
        self.assertEqual(timeparse.timeparse('1.2 minutes'), 72)
        self.assertEqual(timeparse.timeparse('+1.2 minutes'), 72)
        self.assertEqual(timeparse.timeparse('-1.2 minutes'), -72)

    def test_timeparse_22(self):
        '''timeparse test case 22.'''
        self.assertEqual(timeparse.timeparse('172 hours'), 619200)
        self.assertEqual(timeparse.timeparse('+172 hours'), 619200)
        self.assertEqual(timeparse.timeparse('-172 hours'), -619200)

    def test_timeparse_23(self):
        '''timeparse test case 23.'''
        self.assertEqual(timeparse.timeparse('172 hr'), 619200)
        self.assertEqual(timeparse.timeparse('+172 hr'), 619200)
        self.assertEqual(timeparse.timeparse('-172 hr'), -619200)

    def test_timeparse_24(self):
        '''timeparse test case 24.'''
        self.assertEqual(timeparse.timeparse('172 h'), 619200)
        self.assertEqual(timeparse.timeparse('+172 h'), 619200)
        self.assertEqual(timeparse.timeparse('-172 h'), -619200)

    def test_timeparse_25(self):
        '''timeparse test case 25.'''
        self.assertEqual(timeparse.timeparse('172 hrs'), 619200)
        self.assertEqual(timeparse.timeparse('+172 hrs'), 619200)
        self.assertEqual(timeparse.timeparse('-172 hrs'), -619200)

    def test_timeparse_26(self):
        '''timeparse test case 26.'''
        self.assertEqual(timeparse.timeparse('172 hour'), 619200)
        self.assertEqual(timeparse.timeparse('+172 hour'), 619200)
        self.assertEqual(timeparse.timeparse('-172 hour'), -619200)

    def test_timeparse_27(self):
        '''timeparse test case 27.'''
        self.assertEqual(timeparse.timeparse('1.24 days'), 107136)
        self.assertEqual(timeparse.timeparse('+1.24 days'), 107136)
        self.assertEqual(timeparse.timeparse('-1.24 days'), -107136)

    def test_timeparse_28(self):
        '''timeparse test case 28.'''
        self.assertEqual(timeparse.timeparse('5 d'), 432000)
        self.assertEqual(timeparse.timeparse('+5 d'), 432000)
        self.assertEqual(timeparse.timeparse('-5 d'), -432000)

    def test_timeparse_29(self):
        '''timeparse test case 29.'''
        self.assertEqual(timeparse.timeparse('5 day'), 432000)
        self.assertEqual(timeparse.timeparse('+5 day'), 432000)
        self.assertEqual(timeparse.timeparse('-5 day'), -432000)

    def test_timeparse_30(self):
        '''timeparse test case 30.'''
        self.assertEqual(timeparse.timeparse('5 days'), 432000)
        self.assertEqual(timeparse.timeparse('+5 days'), 432000)
        self.assertEqual(timeparse.timeparse('-5 days'), -432000)

    def test_timeparse_31(self):
        '''timeparse test case 31.'''
        self.assertEqual(timeparse.timeparse('5.6 wk'), 3386880)
        self.assertEqual(timeparse.timeparse('+5.6 wk'), 3386880)
        self.assertEqual(timeparse.timeparse('-5.6 wk'), -3386880)

    def test_timeparse_32(self):
        '''timeparse test case 32.'''
        self.assertEqual(timeparse.timeparse('5.6 week'), 3386880)
        self.assertEqual(timeparse.timeparse('+5.6 week'), 3386880)
        self.assertEqual(timeparse.timeparse('-5.6 week'), -3386880)

    def test_timeparse_33(self):
        '''timeparse test case 33.'''
        self.assertEqual(timeparse.timeparse('5.6 weeks'), 3386880)
        self.assertEqual(timeparse.timeparse('+5.6 weeks'), 3386880)
        self.assertEqual(timeparse.timeparse('-5.6 weeks'), -3386880)

    def test_doctest(self):
        '''Run timeparse doctests.'''
        self.assertTrue(doctest.testmod(timeparse, raise_on_error=True))
