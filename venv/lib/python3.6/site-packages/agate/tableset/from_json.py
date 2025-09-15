import json
import os
from collections import OrderedDict
from decimal import Decimal
from glob import glob

from agate.table import Table


@classmethod
def from_json(cls, path, column_names=None, column_types=None, keys=None, **kwargs):
    """
    Create a new :class:`TableSet` from a directory of JSON files or a
    single JSON object with key value (Table key and list of row objects)
    pairs for each :class:`Table`.

    See :meth:`.Table.from_json` for additional details.

    :param path:
        Path to a directory containing JSON files or filepath/file-like
        object of nested JSON file.
    :param keys:
        A list of keys of the top-level dictionaries for each file. If
        specified, length must be equal to number of JSON files in path.
    :param column_types:
        See :meth:`Table.__init__`.
    """
    from agate.tableset import TableSet

    if isinstance(path, str) and not os.path.isdir(path) and not os.path.isfile(path):
        raise OSError('Specified path doesn\'t exist.')

    tables = OrderedDict()

    if isinstance(path, str) and os.path.isdir(path):
        filepaths = glob(os.path.join(path, '*.json'))

        if keys is not None and len(keys) != len(filepaths):
            raise ValueError('If specified, keys must have length equal to number of JSON files')

        for i, filepath in enumerate(filepaths):
            name = os.path.split(filepath)[1].strip('.json')

            if keys is not None:
                tables[name] = Table.from_json(filepath, keys[i], column_types=column_types, **kwargs)
            else:
                tables[name] = Table.from_json(filepath, column_types=column_types, **kwargs)

    else:
        if hasattr(path, 'read'):
            js = json.load(path, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)
        else:
            with open(path) as f:
                js = json.load(f, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)

        for key, value in js.items():
            tables[key] = Table.from_object(value, column_types=column_types, **kwargs)

    return TableSet(tables.values(), tables.keys())
