"""
This module contains agate's :class:`Row` implementation. Rows are independent
of both the :class:`.Table` that contains them as well as the :class:`.Columns`
that access their data. This independence, combined with rows immutability
allows them to be safely shared between table instances.
"""

from agate.mapped_sequence import MappedSequence


class Row(MappedSequence):
    """
    A row of data. Values within a row can be accessed by column name or column
    index. Row are immutable and may be shared between :class:`.Table`
    instances.

    Currently row instances are a no-op subclass of :class:`MappedSequence`.
    They are being maintained in this fashion in order to support future
    features.
    """
    pass
