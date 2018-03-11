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

    def test_tsv(self):
        js = json.loads(self.get_output(['examples/dummy.tsv']))
        self.assertDictEqual(js[0], {'a': True, 'c': 3.0, 'b': 2.0})

    def test_tsv_streaming(self):
        js = json.loads(self.get_output(['--stream', '--no-inference', '--snifflimit', '0', '--tabs', 'examples/dummy.tsv']))
        self.assertDictEqual(js, {'a': '1', 'c': '3', 'b': '2'})

    def test_no_blanks(self):
        js = json.loads(self.get_output(['examples/blanks.csv']))
        self.assertDictEqual(js[0], {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None})

    def test_blanks(self):
        js = json.loads(self.get_output(['--blanks', 'examples/blanks.csv']))
        self.assertDictEqual(js[0], {'a': '', 'b': 'NA', 'c': 'N/A', 'd': 'NONE', 'e': 'NULL', 'f': '.'})

    def test_no_header_row(self):
        js = json.loads(self.get_output(['--no-header-row', 'examples/no_header_row.csv']))
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
        self.assertDictEqual(js, {'True': {'a': True, 'c': 3.0, 'b': 2.0}})

    def test_duplicate_keys(self):
        output_file = six.StringIO()
        utility = CSVJSON(['-k', 'a', 'examples/dummy3.csv'], output_file)
        self.assertRaisesRegex(ValueError, 'Value True is not unique in the key column.', utility.run)
        output_file.close()

    def test_geojson_with_id(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '-k', 'slug', 'examples/test_geo.csv']))

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertNotIn('crs', geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        for feature in geojson['features']:
            self.assertEqual(feature['type'], 'Feature')
            self.assertIn('id', feature)
            self.assertIn('properties', feature)
            self.assertIsInstance(feature['properties'], dict)
            self.assertGreater(len(feature['properties']), 1)

            geometry = feature['geometry']

            self.assertEqual(len(geometry['coordinates']), 2)
            self.assertIsInstance(geometry['coordinates'][0], float)
            self.assertIsInstance(geometry['coordinates'][1], float)

    def test_geojson_point(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', 'examples/test_geo.csv']))

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertNotIn('crs', geojson)
        self.assertEqual(geojson['bbox'], [-95.334619, 32.299076986939205, -95.250699, 32.351434])
        self.assertEqual(len(geojson['features']), 17)

        for feature in geojson['features']:
            self.assertEqual(feature['type'], 'Feature')
            self.assertNotIn('id', feature)
            self.assertIn('properties', feature)
            self.assertIsInstance(feature['properties'], dict)
            self.assertGreater(len(feature['properties']), 1)

            geometry = feature['geometry']

            self.assertEqual(len(geometry['coordinates']), 2)
            self.assertIsInstance(geometry['coordinates'][0], float)
            self.assertIsInstance(geometry['coordinates'][1], float)

    def test_geojson_shape(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '--type', 'type', '--geometry', 'geojson', 'examples/test_geojson.csv']))

        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertNotIn('crs', geojson)
        self.assertEqual(geojson['bbox'], [100.0, 0.0, 105.0, 1.0])
        self.assertEqual(len(geojson['features']), 3)

        for feature in geojson['features']:
            self.assertEqual(feature['type'], 'Feature')
            self.assertNotIn('id', feature)
            self.assertIn('properties', feature)
            self.assertIsInstance(feature['properties'], dict)
            self.assertIn('prop0', feature['properties'].keys())

            geometry = feature['geometry']

            self.assertIn('coordinates', geometry)
            self.assertIsNotNone(geometry['coordinates'])

        self.assertEqual(geojson['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(geojson['features'][1]['geometry']['type'], 'LineString')
        self.assertEqual(geojson['features'][2]['geometry']['type'], 'Polygon')

        self.assertEqual(geojson['features'][0]['geometry']['coordinates'], [102.0, 0.5])
        self.assertEqual(geojson['features'][1]['geometry']['coordinates'],
                         [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]])
        self.assertEqual(geojson['features'][2]['geometry']['coordinates'],
                         [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]])

    def test_geojson_with_crs(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '--crs', 'EPSG:4269', 'examples/test_geo.csv']))
        self.assertIn('crs', geojson)
        self.assertEqual(geojson['crs'], {'type': 'name', 'properties': {'name': 'EPSG:4269'}})

    def test_geojson_with_no_bbox(self):
        geojson = json.loads(self.get_output(['--lat', 'latitude', '--lon', 'longitude', '--no-bbox', 'examples/test_geo.csv']))
        self.assertNotIn('bbox', geojson)

    def test_ndjson(self):
        self.assertLines(['--stream', 'examples/testjson_converted.csv'], [
            '{"text": "Chicago Reader", "float": 1.0, "datetime": "1971-01-01T04:14:00", "boolean": true, "time": "4:14:00", "date": "1971-01-01", "integer": 40.0}',
            '{"text": "Chicago Sun-Times", "float": 1.27, "datetime": "1948-01-01T14:57:13", "boolean": true, "time": "14:57:13", "date": "1948-01-01", "integer": 63.0}',
            '{"text": "Chicago Tribune", "float": 41800000.01, "datetime": "1920-01-01T00:00:00", "boolean": false, "time": "0:00:00", "date": "1920-01-01", "integer": 164.0}',
            '{"text": "This row has blanks", "float": null, "datetime": null, "boolean": null, "time": null, "date": null, "integer": null}',
            '{"text": "Unicode! Σ", "float": null, "datetime": null, "boolean": null, "time": null, "date": null, "integer": null}',
        ])

    def test_ndjson_streaming(self):
        self.assertLines(['--stream', '--no-inference', '--snifflimit', '0', 'examples/testjson_converted.csv'], [
            '{"text": "Chicago Reader", "float": "1.0", "datetime": "1971-01-01T04:14:00", "boolean": "True", "time": "4:14:00", "date": "1971-01-01", "integer": "40"}',
            '{"text": "Chicago Sun-Times", "float": "1.27", "datetime": "1948-01-01T14:57:13", "boolean": "True", "time": "14:57:13", "date": "1948-01-01", "integer": "63"}',
            '{"text": "Chicago Tribune", "float": "41800000.01", "datetime": "1920-01-01T00:00:00", "boolean": "False", "time": "0:00:00", "date": "1920-01-01", "integer": "164"}',
            '{"text": "This row has blanks", "float": "", "datetime": "", "boolean": "", "time": "", "date": "", "integer": ""}',
            '{"text": "Unicode! Σ", "float": "", "datetime": "", "boolean": "", "time": "", "date": "", "integer": ""}',
        ])

    def test_ndgeojson(self):
        self.maxDiff = 5000
        self.assertLines(['--lat', 'latitude', '--lon', 'longitude', '--stream', 'examples/test_geo.csv'], [
            '{"type": "Feature", "properties": {"slug": "dcl", "title": "Downtown Coffee Lounge", "description": "In addition to being the only coffee shop in downtown Tyler, DCL also features regular exhibitions of work by local artists.", "address": "200 West Erwin Street", "type": "Gallery", "last_seen_date": "2012-03-30"}, "geometry": {"type": "Point", "coordinates": [-95.30181, 32.35066]}}',
            '{"type": "Feature", "properties": {"slug": "tyler-museum", "title": "Tyler Museum of Art", "description": "The Tyler Museum of Art on the campus of Tyler Junior College is the largest art museum in Tyler. Visit them online at <a href=\\"http://www.tylermuseum.org/\\">http://www.tylermuseum.org/</a>.", "address": "1300 South Mahon Avenue", "type": "Museum", "last_seen_date": "2012-04-02"}, "geometry": {"type": "Point", "coordinates": [-95.28174, 32.33396]}}',
            '{"type": "Feature", "properties": {"slug": "genecov", "title": "Genecov Sculpture", "description": "Stainless Steel Sculpture", "address": "1350 Dominion Plaza", "type": "Sculpture", "photo_url": "http://i.imgur.com/DICdn.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-04"}, "geometry": {"type": "Point", "coordinates": [-95.31571447849274, 32.299076986939205]}}',
            '{"type": "Feature", "properties": {"slug": "gallery-main-street", "title": "Gallery Main Street", "description": "The only dedicated art gallery in Tyler. Visit them online at <a href=\\"http://www.heartoftyler.com/downtowntylerarts/\\">http://www.heartoftyler.com/downtowntylerarts/</a>.", "address": "110 West Erwin Street", "type": "Gallery", "last_seen_date": "2012-04-09"}, "geometry": {"type": "Point", "coordinates": [-95.30123, 32.35066]}}',
            '{"type": "Feature", "properties": {"slug": "spirit-of-progress", "title": "The Spirit of Progress", "address": "100 block of North Spring Avenue", "type": "Relief", "photo_url": "http://media.hacktyler.com/artmap/photos/spirit-of-progress.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "2012-04-11"}, "geometry": {"type": "Point", "coordinates": [-95.2995, 32.3513]}}',
            '{"type": "Feature", "properties": {"slug": "celestial-conversations-2", "title": "Celestial Conversations #2", "artist": "Simon Saleh", "description": "Steel Sculpture", "address": "100 block of North Spring Avenue", "type": "Sculpture", "photo_url": "http://media.hacktyler.com/artmap/photos/celestial-conversations-2.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "2012-04-11"}, "geometry": {"type": "Point", "coordinates": [-95.2995, 32.351]}}',
            '{"type": "Feature", "properties": {"slug": "pivot-bounce", "title": "Pivot Bounce", "artist": "Chelsea Cope", "address": "100 block of North Spring Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/pmxyi.jpg?1", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-11"}, "geometry": {"type": "Point", "coordinates": [-95.29944, 32.351434]}}',
            '{"type": "Feature", "properties": {"slug": "children-of-peace", "title": "Children of Peace", "artist": "Gary Price", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/rUikO.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.300222, 32.339826]}}',
            '{"type": "Feature", "properties": {"slug": "ross-bears", "title": "Ross\' Bears", "description": "Granite Sculpture", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/SpJQI.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.300034, 32.339776]}}',
            '{"type": "Feature", "properties": {"slug": "butterfly-garden", "title": "Butterfly Garden", "description": "Cast Bronze", "type": "Sculpture", "photo_url": "http://i.imgur.com/0L8DF.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.300219, 32.339559]}}',
            '{"type": "Feature", "properties": {"slug": "goose-fountain", "title": "TJC Goose Fountain", "description": "Copper (?) Sculpture", "address": "1300 S. Mahon Ave.", "type": "Sculpture", "photo_url": "http://i.imgur.com/UWfS6.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.28263, 32.333944]}}',
            '{"type": "Feature", "properties": {"slug": "tjc-cement-totems", "description": "Cast Cement Totems", "address": "1300 S. Mahon Ave.", "type": "Sculpture", "photo_url": "http://i.imgur.com/lRmYd.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.283894, 32.333899]}}',
            '{"type": "Feature", "properties": {"slug": "alison", "title": "Alison", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/7OcrG.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.299887, 32.339809]}}',
            '{"type": "Feature", "properties": {"slug": "jackson", "title": "Jackson", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/aQJfv.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.299939, 32.339828]}}',
            '{"type": "Feature", "properties": {"slug": "505-third", "title": "Untitled", "description": "Stainless Steel", "address": "505 Third St.", "type": "Sculpture", "photo_url": "http://i.imgur.com/0moUY.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.305429, 32.333082]}}',
            '{"type": "Feature", "properties": {"slug": "obeidder", "title": "Obeidder Monster", "description": "Sharpie and Spray Paint", "address": "3319 Seaton St.", "type": "Street Art", "photo_url": "http://i.imgur.com/3aX7E.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "2012-04-15"}, "geometry": {"type": "Point", "coordinates": [-95.334619, 32.314431]}}',
            '{"type": "Feature", "properties": {"slug": "sensor-device", "title": "Sensor Device", "artist": "Kurt Dyrhaug", "address": "University of Texas, Campus Drive", "type": "Sculpture", "photo_url": "http://media.hacktyler.com/artmap/photos/sensor-device.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "2012-04-16"}, "geometry": {"type": "Point", "coordinates": [-95.250699, 32.317216]}}'
        ])

    def test_ndgeojson_streaming(self):
        self.maxDiff = 5000
        self.assertLines(['--stream', '--no-inference', '--snifflimit', '0', '--lat', 'latitude', '--lon', 'longitude', '--stream', 'examples/test_geo.csv'], [
            '{"type": "Feature", "properties": {"slug": "dcl", "title": "Downtown Coffee Lounge", "description": "In addition to being the only coffee shop in downtown Tyler, DCL also features regular exhibitions of work by local artists.", "address": "200 West Erwin Street", "type": "Gallery", "last_seen_date": "3/30/12"}, "geometry": {"type": "Point", "coordinates": [-95.30181, 32.35066]}}',
            '{"type": "Feature", "properties": {"slug": "tyler-museum", "title": "Tyler Museum of Art", "description": "The Tyler Museum of Art on the campus of Tyler Junior College is the largest art museum in Tyler. Visit them online at <a href=\\"http://www.tylermuseum.org/\\">http://www.tylermuseum.org/</a>.", "address": "1300 South Mahon Avenue", "type": "Museum", "last_seen_date": "4/2/12"}, "geometry": {"type": "Point", "coordinates": [-95.28174, 32.33396]}}',
            '{"type": "Feature", "properties": {"slug": "genecov", "title": "Genecov Sculpture", "description": "Stainless Steel Sculpture", "address": "1350 Dominion Plaza", "type": "Sculpture", "photo_url": "http://i.imgur.com/DICdn.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/4/12"}, "geometry": {"type": "Point", "coordinates": [-95.31571447849274, 32.299076986939205]}}',
            '{"type": "Feature", "properties": {"slug": "gallery-main-street", "title": "Gallery Main Street", "description": "The only dedicated art gallery in Tyler. Visit them online at <a href=\\"http://www.heartoftyler.com/downtowntylerarts/\\">http://www.heartoftyler.com/downtowntylerarts/</a>.", "address": "110 West Erwin Street", "type": "Gallery", "last_seen_date": "4/9/12"}, "geometry": {"type": "Point", "coordinates": [-95.30123, 32.35066]}}',
            '{"type": "Feature", "properties": {"slug": "spirit-of-progress", "title": "The Spirit of Progress", "address": "100 block of North Spring Avenue", "type": "Relief", "photo_url": "http://media.hacktyler.com/artmap/photos/spirit-of-progress.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "4/11/12"}, "geometry": {"type": "Point", "coordinates": [-95.2995, 32.3513]}}',
            '{"type": "Feature", "properties": {"slug": "celestial-conversations-2", "title": "Celestial Conversations #2", "artist": "Simon Saleh", "description": "Steel Sculpture", "address": "100 block of North Spring Avenue", "type": "Sculpture", "photo_url": "http://media.hacktyler.com/artmap/photos/celestial-conversations-2.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "4/11/12"}, "geometry": {"type": "Point", "coordinates": [-95.2995, 32.351]}}',
            '{"type": "Feature", "properties": {"slug": "pivot-bounce", "title": "Pivot Bounce", "artist": "Chelsea Cope", "address": "100 block of North Spring Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/pmxyi.jpg?1", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/11/12"}, "geometry": {"type": "Point", "coordinates": [-95.29944, 32.351434]}}',
            '{"type": "Feature", "properties": {"slug": "children-of-peace", "title": "Children of Peace", "artist": "Gary Price", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/rUikO.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.300222, 32.339826]}}',
            '{"type": "Feature", "properties": {"slug": "ross-bears", "title": "Ross\' Bears", "description": "Granite Sculpture", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/SpJQI.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.300034, 32.339776]}}',
            '{"type": "Feature", "properties": {"slug": "butterfly-garden", "title": "Butterfly Garden", "description": "Cast Bronze", "type": "Sculpture", "photo_url": "http://i.imgur.com/0L8DF.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.300219, 32.339559]}}',
            '{"type": "Feature", "properties": {"slug": "goose-fountain", "title": "TJC Goose Fountain", "description": "Copper (?) Sculpture", "address": "1300 S. Mahon Ave.", "type": "Sculpture", "photo_url": "http://i.imgur.com/UWfS6.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.28263, 32.333944]}}',
            '{"type": "Feature", "properties": {"slug": "tjc-cement-totems", "description": "Cast Cement Totems", "address": "1300 S. Mahon Ave.", "type": "Sculpture", "photo_url": "http://i.imgur.com/lRmYd.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.283894, 32.333899]}}',
            '{"type": "Feature", "properties": {"slug": "alison", "title": "Alison", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/7OcrG.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.299887, 32.339809]}}',
            '{"type": "Feature", "properties": {"slug": "jackson", "title": "Jackson", "description": "Cast Bronze", "address": "900 South Broadway Avenue", "type": "Sculpture", "photo_url": "http://i.imgur.com/aQJfv.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.299939, 32.339828]}}',
            '{"type": "Feature", "properties": {"slug": "505-third", "title": "Untitled", "description": "Stainless Steel", "address": "505 Third St.", "type": "Sculpture", "photo_url": "http://i.imgur.com/0moUY.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.305429, 32.333082]}}',
            '{"type": "Feature", "properties": {"slug": "obeidder", "title": "Obeidder Monster", "description": "Sharpie and Spray Paint", "address": "3319 Seaton St.", "type": "Street Art", "photo_url": "http://i.imgur.com/3aX7E.jpg", "photo_credit": "Photo by Justin Edwards. Used with permission.", "last_seen_date": "4/15/12"}, "geometry": {"type": "Point", "coordinates": [-95.334619, 32.314431]}}',
            '{"type": "Feature", "properties": {"slug": "sensor-device", "title": "Sensor Device", "artist": "Kurt Dyrhaug", "address": "University of Texas, Campus Drive", "type": "Sculpture", "photo_url": "http://media.hacktyler.com/artmap/photos/sensor-device.jpg", "photo_credit": "Photo by Christopher Groskopf. Used with permission.", "last_seen_date": "4/16/12"}, "geometry": {"type": "Point", "coordinates": [-95.250699, 32.317216]}}'
        ])


