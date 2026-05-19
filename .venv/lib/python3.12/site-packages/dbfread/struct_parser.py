"""
Parser that converts (C style) binary structs named tuples.

The struct can be read from a file or a byte string.
"""

import struct
import collections


def _make_struct_class(name, names):
    class Struct(object):
        _names = names
        def __init__(self, **kwargs):
            vars(self).update(kwargs)

        def __repr__(self):
            fields = ', '.join('{}={!r}'.format(name, getattr(self, name))
                               for name in self._names)
            return '{}({})'.format(self.__class__.__name__, fields)

    Struct.__name__ = name
    return Struct


class StructParser:
    def __init__(self, name, format, names):
        self.format = format
        self.names = names
        self.struct = struct.Struct(format)
        self.Class = _make_struct_class(name, names)
        self.size = self.struct.size

    def unpack(self, data):
        """Unpack struct from binary string and return a named tuple."""
        items = zip(self.names, self.struct.unpack(data))
        return self.Class(**dict(items))

    def read(self, file):
        """Read struct from a file-like object (implenting read())."""
        return self.unpack(file.read(self.struct.size))
