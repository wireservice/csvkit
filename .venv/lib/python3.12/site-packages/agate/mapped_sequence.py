"""
This module contains the :class:`MappedSequence` class that forms the foundation
for agate's :class:`.Row` and :class:`.Column` as well as for named sequences of
rows and columns.
"""

from collections import OrderedDict
from collections.abc import Sequence

from agate.utils import memoize


class MappedSequence(Sequence):
    """
    A generic container for immutable data that can be accessed either by
    numeric index or by key. This is similar to an
    :class:`collections.OrderedDict` except that the keys are optional and
    iteration over it returns the values instead of keys.

    This is the base class for both :class:`.Column` and :class:`.Row`.

    :param values:
        A sequence of values.
    :param keys:
        A sequence of keys.
    """
    __slots__ = ['_values', '_keys']

    def __init__(self, values, keys=None):
        self._values = tuple(values)

        if keys is not None:
            self._keys = keys
        else:
            self._keys = None

    def __getstate__(self):
        """
        Return state values to be pickled.

        This is necessary on Python2.7 when using :code:`__slots__`.
        """
        return {
            '_values': self._values,
            '_keys': self._keys
        }

    def __setstate__(self, data):
        """
        Restore pickled state.

        This is necessary on Python2.7 when using :code:`__slots__`.
        """
        self._values = data['_values']
        self._keys = data['_keys']

    def __unicode__(self):
        """
        Print a unicode sample of the contents of this sequence.
        """
        sample = ', '.join(repr(d) for d in self.values()[:5])

        if len(self) > 5:
            sample = '%s, ...' % sample

        return f'<agate.{type(self).__name__}: ({sample})>'

    def __str__(self):
        """
        Print an ascii sample of the contents of this sequence.
        """
        return str(self.__unicode__())

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        """
        Retrieve values from this array by index, slice or key.
        """
        if isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            values = self.values()
            return tuple(values[i] for i in indices)
        # Note: can't use isinstance because bool is a subclass of int
        elif type(key) is int:
            return self.values()[key]
        return self.dict()[key]

    def __setitem__(self, key, value):
        """
        Set values by index, which we want to fail loudly.
        """
        raise TypeError('Rows and columns can not be modified directly. You probably need to compute a new column.')

    def __iter__(self):
        """
        Iterate over values.
        """
        return iter(self.values())

    @memoize
    def __len__(self):
        return len(self.values())

    def __eq__(self, other):
        """
        Equality test with other sequences.
        """
        if not isinstance(other, Sequence):
            return False

        return self.values() == tuple(other)

    def __ne__(self, other):
        """
        Inequality test with other sequences.
        """
        return not self.__eq__(other)

    def __contains__(self, value):
        return self.values().__contains__(value)

    def keys(self):
        """
        Equivalent to :meth:`collections.OrderedDict.keys`.
        """
        return self._keys

    def values(self):
        """
        Equivalent to :meth:`collections.OrderedDict.values`.
        """
        return self._values

    @memoize
    def items(self):
        """
        Equivalent to :meth:`collections.OrderedDict.items`.
        """
        return tuple(zip(self.keys(), self.values()))

    def get(self, key, default=None):
        """
        Equivalent to :meth:`collections.OrderedDict.get`.
        """
        try:
            return self.dict()[key]
        except KeyError:
            if default:
                return default
            return None

    @memoize
    def dict(self):
        """
        Retrieve the contents of this sequence as an
        :class:`collections.OrderedDict`.
        """
        if self.keys() is None:
            raise KeyError

        return OrderedDict(self.items())
