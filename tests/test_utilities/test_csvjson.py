#!/usr/bin/env python

import json

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit.exceptions import NonUniqueKeyColumnException
from csvkit.utilities.csvjson import CSVJSON

class TestCSVJSON(unittest.TestCase):
    def test_simple(self):
        args = ['examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVJSON(args, output_file)
        utility.main()

        js = json.loads(output_file.getvalue())

        self.assertDictEqual(js[0], {"a": "1", "c": "3", "b": "2"})

    def test_indentation(self):
        args = ['-i', '4', 'examples/dummy.csv']
        output_file = six.StringIO()

        utility = CSVJSON(args, output_file)
        utility.main()

        js = json.loads(output_file.getvalue())

        self.assertDictEqual(js[0], {"a": "1", "c": "3", "b": "2"})

    def test_keying(self):
        args = ['-k', 'a', 'examples/dummy.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()

        js = json.loads(output_file.getvalue())

        self.assertDictEqual(js, { "1": {"a": "1", "c": "3", "b": "2"} })

    def test_duplicate_keys(self):
        args = ['-k', 'a', 'examples/dummy3.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)

        self.assertRaises(NonUniqueKeyColumnException, utility.main)

    def test_geojson(self):
        args = ['--lat', 'latitude', '--lon', 'longitude', 'examples/test_geo.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()

        geojson = json.loads(output_file.getvalue())

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertFalse('crs' in geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        for feature in geojson['features']:
            self.assertEqual(feature['type'], 'Feature')
            self.assertFalse('id' in feature)
            self.assertEqual(len(feature['properties']), 10)
            
            geometry = feature['geometry']

            self.assertEqual(len(geometry['coordinates']), 2)
            self.assertTrue(isinstance(geometry['coordinates'][0], float))
            self.assertTrue(isinstance(geometry['coordinates'][1], float))

    def test_geojson_with_id(self):
        args = ['--lat', 'latitude', '--lon', 'longitude', '-k', 'slug', 'examples/test_geo.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()

        geojson = json.loads(output_file.getvalue())

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertFalse('crs' in geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        for feature in geojson['features']:
            self.assertEqual(feature['type'], 'Feature')
            self.assertTrue('id' in feature)
            self.assertEqual(len(feature['properties']), 9)
            
            geometry = feature['geometry']

            self.assertEqual(len(geometry['coordinates']), 2)
            self.assertTrue(isinstance(geometry['coordinates'][0], float))
            self.assertTrue(isinstance(geometry['coordinates'][1], float))

    def test_geojson_with_crs(self):
        args = ['--lat', 'latitude', '--lon', 'longitude', '--crs', 'EPSG:4269', 'examples/test_geo.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()

        geojson = json.loads(output_file.getvalue())

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertTrue('crs' in geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        crs = geojson['crs']

        self.assertEqual(crs['type'], 'name')
        self.assertEqual(crs['properties']['name'], 'EPSG:4269')

    def test_json_streaming(self):
        args = ['--stream', 'examples/dummy3.csv']
        output_file = six.StringIO()
        
        utility = CSVJSON(args, output_file)
        utility.main()
        
        result = list(map(json.loads, output_file.getvalue().splitlines()))
        self.assertEqual(len(result), 2)
        self.assertDictEqual(result[0], {"a": "1", "c": "3", "b": "2"})
        self.assertDictEqual(result[1], {"a": "1", "c": "5", "b": "4"})

