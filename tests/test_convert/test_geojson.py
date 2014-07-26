#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.convert import geojs

class TestGeoJSON(unittest.TestCase):
    def test_geojson(self):
        with open('examples/test_geojson.json', 'rt') as f:
            output = geojs.geojson2csv(f)

        self.assertIn('id,prop0,prop1,geojson', output)
        self.assertIn('""coordinates"": [102.0, 0.5]', output)
        self.assertIn('""coordinates"": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]]', output)

