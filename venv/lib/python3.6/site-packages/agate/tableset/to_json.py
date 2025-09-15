import json
import os
from collections import OrderedDict
from io import StringIO


def to_json(self, path, nested=False, indent=None, **kwargs):
    """
    Write :class:`TableSet` to either a set of JSON files for each table or
    a single nested JSON file.

    See :meth:`.Table.to_json` for additional details.

    :param path:
        Path to the directory to write the JSON file(s) to. If nested is
        `True`, this should be a file path or file-like object to write to.
    :param nested:
        If `True`, the output will be a single nested JSON file with each
        Table's key paired with a list of row objects. Otherwise, the output
        will be a set of files for each table. Defaults to `False`.
    :param indent:
        See :meth:`Table.to_json`.
    """
    if not nested:
        if not os.path.exists(path):
            os.makedirs(path)

        for name, table in self.items():
            filepath = os.path.join(path, '%s.json' % name)

            table.to_json(filepath, indent=indent, **kwargs)
    else:
        close = True
        tableset_dict = OrderedDict()

        for name, table in self.items():
            output = StringIO()
            table.to_json(output, **kwargs)
            tableset_dict[name] = json.loads(output.getvalue(), object_pairs_hook=OrderedDict)

        if hasattr(path, 'write'):
            f = path
            close = False
        else:
            dirpath = os.path.dirname(path)

            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath)

            f = open(path, 'w')

        json_kwargs = {'ensure_ascii': False, 'indent': indent}

        json_kwargs.update(kwargs)
        json.dump(tableset_dict, f, **json_kwargs)

        if close and f is not None:
            f.close()
