from decimal import Decimal

from leather.scales.base import Scale


class Ordinal(Scale):
    """
    A scale that maps individual values (e.g. strings) to a range.
    """
    def __init__(self, domain):
        self._domain = domain

    def contains(self, v):
        """
        Return :code:`True` if a given value is contained within this scale's
        displayed domain.
        """
        return v in self._domain

    def project(self, value, range_min, range_max):
        """
        Project a value in this scale's domain to a target range.
        """
        range_min = Decimal(range_min)
        range_max = Decimal(range_max)

        segments = len(self._domain)
        segment_size = (range_max - range_min) / segments

        try:
            pos = range_min + (self._domain.index(value) * segment_size) + (segment_size / 2)
        except ValueError:
            raise ValueError('Value "%s" is not present in Ordinal scale domain' % value)

        return pos

    def project_interval(self, value, range_min, range_max):
        """
        Project a value in this scale's domain to an interval in the target
        range. This is used for places :class:`.Bars` and :class:`.Columns`.
        """
        range_min = Decimal(range_min)
        range_max = Decimal(range_max)

        segments = len(self._domain)
        segment_size = (range_max - range_min) / segments
        gap = segment_size / Decimal(20)

        try:
            a = range_min + (self._domain.index(value) * segment_size) + gap
            b = range_min + ((self._domain.index(value) + 1) * segment_size) - gap
        except ValueError:
            raise ValueError('Value "%s" is not present in Ordinal scale domain' % value)

        return (a, b)

    def ticks(self):
        """
        Generate a series of ticks for this scale.
        """
        return self._domain
