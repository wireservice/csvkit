#!/usr/bin/env python

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import six

from csvkit import CSVKitWriter

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
        geoid = feature.get('id', None)

        properties = feature.get('properties') or {}

        for prop in properties.keys():
            if prop not in property_fields:
                property_fields.append(prop)

        geometry = json.dumps(feature['geometry'])

        features_parsed.append((geoid, properties, geometry))

    header = ['id']
    header.extend(property_fields)
    header.append('geojson')

    o = six.StringIO()
    writer = CSVKitWriter(o)

    writer.writerow(header)

    for geoid, properties, geometry in features_parsed:
        row = [geoid]

        for field in property_fields:
            row.append(properties.get(field, None))

        row.append(geometry)

        writer.writerow(row)

    output = o.getvalue()
    o.close()

    return output

