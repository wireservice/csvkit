#!/usr/bin/env python

import json
import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvjson import CSVJSON, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVJSON(CSVKitTestCase, EmptyFileTests):
    Utility = CSVJSON

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        js = json.loads(self.get_output(['examples/dummy.csv']))
        self.assertDictEqual(js[0], {'a': True, 'c': 3.0, 'b': 2.0})

    def test_sniff_limit(self):
        js = json.loads(self.get_output(['examples/sniff_limit.csv']))
        self.assertDictEqual(js[0], {'a': True, 'c': 3.0, 'b': 2.0})

    def test_no_inference(self):
        js = json.loads(self.get_output(['--no-inference', 'examples/dummy.csv']))
        self.assertDictEqual(js[0], {'a': '1', 'c': '3', 'b': '2'})

    def test_indentation(self):
        output = self.get_output(['-i', '4', 'examples/dummy.csv'])
        js = json.loads(output)
        self.assertDictEqual(js[0], {'a': True, 'c': 3.0, 'b': 2.0})
        self.assertRegexpMatches(output, '        "a": true,')

    def test_keying(self):
        js = json.loads(self.get_output(['-k', 'a', 'examples/dummy.csv']))
        self.assertDictEqual(js, {'true': {'a': True, 'c': 3.0, 'b': 2.0}})

    def test_duplicate_keys(self):
        utility = CSVJSON(['-k', 'a', 'examples/dummy3.csv'], six.StringIO())
        self.assertRaisesRegexp(ValueError, 'Value True is not unique in the key column\.', utility.main)

    def test_geojson(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', 'examples/test_geo.csv']))

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
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '-k', 'slug', 'examples/test_geo.csv']))

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
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '--crs', 'EPSG:4269', 'examples/test_geo.csv']))

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertTrue('crs' in geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        crs = geojson['crs']

        self.assertEqual(crs['type'], 'name')
        self.assertEqual(crs['properties']['name'], 'EPSG:4269')

    def test_json_streaming(self):
        output = self.get_output(['--stream', 'examples/dummy3.csv'])
        result = list(map(json.loads, output.splitlines()))
        self.assertEqual(len(result), 2)
        self.assertDictEqual(result[0], {'a': True, 'c': 3.0, 'b': 2.0})
        self.assertDictEqual(result[1], {'a': True, 'c': 5.0, 'b': 4.0})
