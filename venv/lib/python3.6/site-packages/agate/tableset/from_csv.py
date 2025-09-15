import os
from collections import OrderedDict
from glob import glob

from agate.table import Table


@classmethod
def from_csv(cls, dir_path, column_names=None, column_types=None, row_names=None, header=True, **kwargs):
    """
    Create a new :class:`TableSet` from a directory of CSVs.

    See :meth:`.Table.from_csv` for additional details.

    :param dir_path:
        Path to a directory full of CSV files. All CSV files in this
        directory will be loaded.
    :param column_names:
        See :meth:`Table.__init__`.
    :param column_types:
        See :meth:`Table.__init__`.
    :param row_names:
        See :meth:`Table.__init__`.
    :param header:
        See :meth:`Table.from_csv`.
    """
    from agate.tableset import TableSet

    if not os.path.isdir(dir_path):
        raise OSError('Specified path doesn\'t exist or isn\'t a directory.')

    tables = OrderedDict()

    for path in glob(os.path.join(dir_path, '*.csv')):
        name = os.path.split(path)[1].strip('.csv')

        tables[name] = Table.from_csv(path, column_names, column_types, row_names=row_names, header=header, **kwargs)

    return TableSet(tables.values(), tables.keys())
