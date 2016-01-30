#!/usr/bin/env python

import agate
import six


def json2csv(f, key=None, newline=False, **kwargs):
    """
    Create a new table from a JSON file. Contents should be an array
    containing a dictionary for each "row". Nested objects or lists will
    also be parsed. For example, this object:

    .. code-block:: javascript

        {
            'one': {
                'a': 1,
                'b': 2,
                'c': 3
            },
            'two': [4, 5, 6],
            'three': 'd'
        }

    Would generate these columns and values:

    .. code-block:: python

        {
            'one/a': 1,
            'one/b': 2,
            'one/c': 3,
            'two.0': 4,
            'two.1': 5,
            'two.2': 6,
            'three': 'd'
        }

    Column names and types will be inferred from the data. Not all rows are
    required to have the same keys. Missing elements will be filled in with
    null.

    If the file contains a top-level dictionary you may specify what
    property contains the row list using the `key` parameter.
    """

    # The documentation above is copied from `agate.Table.from_json`.

    table = agate.Table.from_json(f, key=key, newline=newline, **kwargs)

    output = six.StringIO()
    table.to_csv(output)
    result = output.getvalue()
    output.close()

    return result
