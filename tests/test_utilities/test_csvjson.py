#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.assertRegex(output, '        "a": true,')

    def test_keying(self):
        js = json.loads(self.get_output(['-k', 'a', 'examples/dummy.csv']))
        self.assertDictEqual(js, {'true': {'a': True, 'c': 3.0, 'b': 2.0}})

    def test_duplicate_keys(self):
        output_file = six.StringIO()
        utility = CSVJSON(['-k', 'a', 'examples/dummy3.csv'], output_file)
        self.assertRaisesRegex(ValueError, 'Value True is not unique in the key column.', utility.run)
        output_file.close()

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

    def test_ndjson(self):
        self.assertLines(['--stream', 'examples/testjson_converted.csv'], [
            '{"text": "Chicago Reader", "float": 1.0, "datetime": "1971-01-01T04:14:00", "boolean": true, "time": "4:14:00", "date": "1971-01-01", "integer": 40.0}',
            '{"text": "Chicago Sun-Times", "float": 1.27, "datetime": "1948-01-01T14:57:13", "boolean": true, "time": "14:57:13", "date": "1948-01-01", "integer": 63.0}',
            '{"text": "Chicago Tribune", "float": 41800000.01, "datetime": "1920-01-01T00:00:00", "boolean": false, "time": "0:00:00", "date": "1920-01-01", "integer": 164.0}',
            '{"text": "This row has blanks", "float": null, "datetime": null, "boolean": null, "time": null, "date": null, "integer": null}',
            '{"text": "Unicode! Σ", "float": null, "datetime": null, "boolean": null, "time": null, "date": null, "integer": null}',
        ])

    def test_ndjson_with_no_inference(self):
        self.assertLines(['--stream', '--no-inference', 'examples/testjson_converted.csv'], [
            '{"text": "Chicago Reader", "float": "1.0", "datetime": "1971-01-01T04:14:00", "boolean": "True", "time": "4:14:00", "date": "1971-01-01", "integer": "40"}',
            '{"text": "Chicago Sun-Times", "float": "1.27", "datetime": "1948-01-01T14:57:13", "boolean": "True", "time": "14:57:13", "date": "1948-01-01", "integer": "63"}',
            '{"text": "Chicago Tribune", "float": "41800000.01", "datetime": "1920-01-01T00:00:00", "boolean": "False", "time": "0:00:00", "date": "1920-01-01", "integer": "164"}',
            '{"text": "This row has blanks", "float": "", "datetime": "", "boolean": "", "time": "", "date": "", "integer": ""}',
            '{"text": "Unicode! Σ", "float": "", "datetime": "", "boolean": "", "time": "", "date": "", "integer": ""}',
        ])
