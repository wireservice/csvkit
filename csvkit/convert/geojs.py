#!/usr/bin/env python

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import agate
import six


def geojson2csv(f, key=None, **kwargs):
    """
    Convert a GeoJSON document into CSV format.
    """
    js = json.load(f, object_pairs_hook=OrderedDict)

    if not isinstance(js, dict):
        raise TypeError('JSON document is not valid GeoJSON: Root element is not an object.')

    if 'type' not in js:
        raise TypeError('JSON document is not valid GeoJSON: No top-level "type" key.')

    if js['type'] != 'FeatureCollection':
        raise TypeError('Only GeoJSON with root FeatureCollection type is supported. Not %s' % js['type'])

    if 'features' not in js:
        raise TypeError('JSON document is not a valid FeatureCollection: No top-level "features" key.')

    features = js['features']

    features_parsed = []    # tuples in the format (id, properties, geometry)
    property_fields = []

    for feature in features:
        properties = feature.get('properties', {})

        for prop in properties.keys():
            if prop not in property_fields:
                property_fields.append(prop)

        geometry = feature['geometry']
        geometry_type = geometry.get('type')
        if geometry_type == 'Point':
            longitude, latitude = geometry['coordinates']
        else:
            longitude, latitude = (None, None)

        features_parsed.append((feature.get('id'), properties, json.dumps(geometry), geometry_type, longitude, latitude))

    header = ['id']
    header.extend(property_fields)
    header.extend(('geojson', 'type', 'longitude', 'latitude'))

    o = six.StringIO()
    writer = agate.csv.writer(o)

    writer.writerow(header)

    for geoid, properties, geometry, geometry_type, longitude, latitude in features_parsed:
        row = [geoid]

        for field in property_fields:
            value = properties.get(field)
            if isinstance(value, OrderedDict):
                value = json.dumps(value)
            row.append(value)

        row.extend((geometry, geometry_type, longitude, latitude))

        writer.writerow(row)

    output = o.getvalue()
    o.close()

    return output
