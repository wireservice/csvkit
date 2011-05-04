#!/usr/bin/env python

from cStringIO import StringIO
import json

from csvkit import CSVKitWriter

def parse_object(obj, path=''):
    """
    Recursively parse JSON objects and a dictionary of paths/keys and values.

    Inspired by JSONPipe (https://github.com/dvxhouse/jsonpipe).
    """
    if isinstance(obj, dict):
        iterator = obj.iteritems()
    elif isinstance(obj, (list, tuple)):
        iterator = enumerate(obj)
    else:
        return { path.strip('/'): obj }

    d = {}

    for key, value in iterator:
        key = unicode(key)
        d.update(parse_object(value, path + key + '/'))

    return d

def json2csv(f, key=None, **kwargs):
    """
    Convert a JSON document into CSV format.

    The top-level element of the input must be a list or a dictionary. If it is a dictionary, a key must be provided which is an item of the dictionary which contains a list.
    """
    document = f.read()
    js = json.loads(document)

    if isinstance(js, dict):
        if not key:
            raise TypeError('When converting a JSON document with a top-level dictionary element, a key must be specified.')
        
        js = js[key]

    if not isinstance(js, list):
        raise TypeError('Only JSON documents with a top-level list element are able to be converted (or a top-level dictionary if specifying a key).')

    field_set = set()
    flat = []

    for obj in js:
        flat.append(parse_object(obj)) 

    for obj in flat:
        field_set.update(obj.keys())

    fields = sorted(list(field_set))

    o = StringIO()
    writer = CSVKitWriter(o)

    writer.writerow(fields)

    for i in flat:
        row = []

        for field in fields:
            if field in i:
                row.append(i[field])
            else:
                row.append(None)

        writer.writerow(row)

    output = o.getvalue()
    o.close()

    return output

