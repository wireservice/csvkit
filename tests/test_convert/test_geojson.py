#!/usr/bin/env python

import six

from csvkit.convert import geojs
from csvkit.utilities.in2csv import In2CSV
from tests.utils import CSVKitTestCase, stdin_as_string


class TestGeoJSON(CSVKitTestCase):
    Utility = In2CSV

    def test_geojson(self):
        with open('examples/test_geojson.json', 'rt') as f:
            output = geojs.geojson2csv(f)

        self.assertIn('id,prop0,prop1,geojson', output)
        self.assertIn('""coordinates"": [102.0, 0.5]', output)
        self.assertIn('""coordinates"": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]]', output)

    def test_geojson_no_inference(self):
        input_file = six.StringIO('{"a": 1, "b": 2, "type": "FeatureCollection", "features": [{"geometry": {}, "properties": {"a": 1, "b": 2, "c": 3}}]}')

        with stdin_as_string(input_file):
            self.assertLines(['--no-inference', '-f', 'geojson'], [
                'id,a,b,c,geojson',
                ',1,2,3,{}',
            ])
