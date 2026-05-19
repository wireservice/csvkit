from agate import utils


@classmethod
def from_object(cls, obj, row_names=None, column_types=None):
    """
    Create a new table from a Python object.

    The object should be a list containing a dictionary for each "row".
    Nested objects or lists will also be parsed. For example, this object:

    .. code-block:: python

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

    Column names and types will be inferred from the data.

    Not all rows are required to have the same keys. Missing elements will
    be filled in with null values.

    Keys containing a slash (``/``) can collide with other keys. For example:

    .. code-block:: python

        {
            'a/b': 2,
            'a': {
                'b': False
            }
        }

    Would generate:

    .. code-block:: python

        {
            'a/b': false
        }

    :param obj:
        Filepath or file-like object from which to read JSON data.
    :param row_names:
        See :meth:`.Table.__init__`.
    :param column_types:
        See :meth:`.Table.__init__`.
    """
    from agate.table import Table

    column_names = []
    row_objects = []

    for sub in obj:
        parsed = utils.parse_object(sub)

        for key in parsed.keys():
            if key not in column_names:
                column_names.append(key)

        row_objects.append(parsed)

    rows = []

    for sub in row_objects:
        r = []

        for name in column_names:
            r.append(sub.get(name, None))

        rows.append(r)

    return Table(rows, column_names, row_names=row_names, column_types=column_types)
