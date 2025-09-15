"""
This module contains the DBF extension to :class:`Table <agate.table.Table>`.
"""

import agate
from dbfread import DBF


def recfactory(items):
    return tuple(kv[1] for kv in items)


def from_dbf(cls, path, encoding=None):
    """
    Parse a DBF file.

    :param path:
        Path to an DBF file to load. Note that due to limitations of the
        dependency you can not pass a file handle. It must be a path.
    """
    dbf = DBF(path, load=True, encoding=encoding, recfactory=recfactory)
    table = agate.Table(dbf.records, column_names=dbf.field_names)

    return table


agate.Table.from_dbf = classmethod(from_dbf)
