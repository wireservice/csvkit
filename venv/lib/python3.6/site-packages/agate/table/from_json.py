import json
from collections import OrderedDict
from decimal import Decimal


@classmethod
def from_json(cls, path, row_names=None, key=None, newline=False, column_types=None, encoding='utf-8', **kwargs):
    """
    Create a new table from a JSON file.

    Once the JSON has been deseralized, the resulting Python object is
    passed to :meth:`.Table.from_object`.

    If the file contains a top-level dictionary you may specify what
    property contains the row list using the :code:`key` parameter.

    :code:`kwargs` will be passed through to :meth:`json.load`.

    :param path:
        Filepath or file-like object from which to read JSON data.
    :param row_names:
        See the :meth:`.Table.__init__`.
    :param key:
        The key of the top-level dictionary that contains a list of row
        arrays.
    :param newline:
        If `True` then the file will be parsed as "newline-delimited JSON".
    :param column_types:
        See :meth:`.Table.__init__`.
    :param encoding:
        According to RFC4627, JSON text shall be encoded in Unicode; the default encoding is
        UTF-8. You can override this by using any encoding supported by your Python's open() function
        if :code:`path` is a filepath. If passing in a file handle, it is assumed you have already opened it with the
        correct encoding specified.
    """
    from agate.table import Table

    if key is not None and newline:
        raise ValueError('key and newline may not be specified together.')

    close = False

    try:
        if newline:
            js = []

            if hasattr(path, 'read'):
                for line in path:
                    js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
            else:
                f = open(path, encoding=encoding)
                close = True

                for line in f:
                    js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
        else:
            if hasattr(path, 'read'):
                js = json.load(path, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)
            else:
                f = open(path, encoding=encoding)
                close = True

                js = json.load(f, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)

        if isinstance(js, dict):
            if not key:
                raise TypeError(
                    'When converting a JSON document with a top-level dictionary element, a key must be specified.'
                )

            js = js[key]

    finally:
        if close:
            f.close()

    return Table.from_object(js, row_names=row_names, column_types=column_types)
