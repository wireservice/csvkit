#!/usr/bin/env python

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import itertools
import six

from csvkit import CSVKitWriter

def parse_object(obj, path=''):
    """
    Recursively parse JSON objects and a dictionary of paths/keys and values.

    Inspired by JSONPipe (https://github.com/dvxhouse/jsonpipe).
    """
    if isinstance(obj, dict):
        iterator = obj.items()
    elif isinstance(obj, (list, tuple)):
        iterator = enumerate(obj)
    else:
        stripped_path = path.strip('/')
        return ([stripped_path],{stripped_path: obj})

    d = {}
    f = []

    for key, value in iterator:
        key = six.text_type(key)
        (f1,d1) = parse_object(value, path + key + '/')
        f.extend(f1)
        d.update(d1)

    return (f, d)

def json2csv(f, field=None, **kwargs):
    """
    Convert a JSON document into CSV format.

    The top-level element of the input must be a list or a dictionary. If it is a dictionary, a key must be provided which is an item of the dictionary which contains a list.
    """
    js = json.load(f, object_pairs_hook=OrderedDict)

    if isinstance(js, dict):
        if not field:
            raise TypeError('When converting a JSON document with a top-level dictionary element, a key must be specified.')

        js = js[field]

    fields = []
    flats = []

    for obj in js:
        (flat_fields, flat_key_values_dict) = parse_object(obj)
        flats.append(flat_key_values_dict)

        for field in flat_fields:
            if field not in fields:
                fields.append(field)

    o = six.StringIO()
    writer = CSVKitWriter(o)

    writer.writerow(fields)

    for i in flats:
        row = []

        for field in fields:
            row.append(i.get(field, None))

        writer.writerow(row)

    output = o.getvalue()
    o.close()

    return output

