#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

if six.PY2:
    from csvkit.convert import dbase

@unittest.skipUnless(six.PY2, "Only supported in Python 2.")
class TestDBF(unittest.TestCase):
    def test_dbf(self):
        with open('examples/testdbf.dbf', 'rb') as f:
            output = dbase.dbf2csv(f)

        with open('examples/testdbf_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

