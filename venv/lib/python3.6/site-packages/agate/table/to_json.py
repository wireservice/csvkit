import json
import os
from collections import OrderedDict
from decimal import Decimal


def to_json(self, path, key=None, newline=False, indent=None, **kwargs):
    """
    Write this table to a JSON file or file-like object.

    :code:`kwargs` will be passed through to the JSON encoder.

    :param path:
        File path or file-like object to write to.
    :param key:
        If specified, JSON will be output as an hash instead of a list. May
        be either the name of a column from the this table containing
        unique values or a :class:`function` that takes a row and returns
        a unique value.
    :param newline:
        If `True`, output will be in the form of "newline-delimited JSON".
    :param indent:
        If specified, the number of spaces to indent the JSON for
        formatting.
    """
    if key is not None and newline:
        raise ValueError('key and newline may not be specified together.')

    if newline and indent is not None:
        raise ValueError('newline and indent may not be specified together.')

    key_is_row_function = hasattr(key, '__call__')

    json_kwargs = {
        'ensure_ascii': False,
        'indent': indent
    }

    # Pass remaining kwargs through to JSON encoder
    json_kwargs.update(kwargs)

    json_funcs = [c.jsonify for c in self._column_types]

    close = True
    f = None

    try:
        if hasattr(path, 'write'):
            f = path
            close = False
        else:
            if os.path.dirname(path) and not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            f = open(path, 'w')

        def dump_json(data):
            json.dump(data, f, **json_kwargs)

            if newline:
                f.write('\n')

        # Keyed
        if key is not None:
            output = OrderedDict()

            for row in self._rows:
                if key_is_row_function:
                    k = key(row)
                elif isinstance(row[key], Decimal):
                    k = str(row[key].normalize())
                else:
                    k = str(row[key])

                if k in output:
                    raise ValueError('Value %s is not unique in the key column.' % str(k))

                values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                output[k] = OrderedDict(zip(row.keys(), values))
            dump_json(output)
        # Newline-delimited
        elif newline:
            for row in self._rows:
                values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                dump_json(OrderedDict(zip(row.keys(), values)))
        # Normal
        else:
            output = []

            for row in self._rows:
                values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                output.append(OrderedDict(zip(row.keys(), values)))

            dump_json(output)
    finally:
        if close and f is not None:
            f.close()
