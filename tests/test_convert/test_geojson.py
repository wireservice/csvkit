#!/usr/bin/env python

import unittest

from csvkit.convert import geojs

class TestGeoJSON(unittest.TestCase):
    def test_dbf(self):
        with open('examples/test_geojson.json', 'rb') as f:
            output = geojs.geojson2csv(f)

        with open('examples/test_geojson.csv', 'r') as f:
            self.assertEquals(f.read(), output)

