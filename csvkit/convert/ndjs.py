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
        return { path.strip('/'): obj }

    d = {}

    for key, value in iterator:
        key = six.text_type(key)
        d.update(parse_object(value, path + key + '/'))

    return d

def ndjson2csv(f, key=None, **kwargs):
    """
    Convert a JSON document into CSV format.

    Supports both JSON and "Newline-delimited JSON".

    The top-level element of the input must be a list or a dictionary. If it is a dictionary, a key must be provided which is an item of the dictionary which contains a list.
    """
    first_line = f.readline()

    first_row = json.loads(first_line, object_pairs_hook=OrderedDict)
    js = itertools.chain((first_row, ), (json.loads(l, object_pairs_hook=OrderedDict) for l in f))

    fields = []
    flat = []

    for obj in js:
        flat.append(parse_object(obj)) 

        for key in obj.keys():
            if key not in fields:
                fields.append(key)

    o = six.StringIO()
    writer = CSVKitWriter(o)

    writer.writerow(fields)

    for i in flat:
        row = []

        for field in fields:
            row.append(i.get(field, None))

        writer.writerow(row)

    output = o.getvalue()
    o.close()

    return output

