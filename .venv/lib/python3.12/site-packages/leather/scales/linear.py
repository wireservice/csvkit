from decimal import Decimal

from leather.scales.base import Scale
from leather.ticks.score import ScoreTicker


class Linear(Scale):
    """
    A scale that linearly maps values from a domain to a range.

    :param domain_min:
        The minimum value of the input domain.
    :param domain_max:
        The maximum value of the input domain.
    """
    def __init__(self, domain_min, domain_max):
        if domain_min > domain_max:
            raise ValueError('Inverted domains are not currently supported.')
        elif domain_min == domain_max:
            # Default to unit scale
            self._data_min = Decimal(0)
            self._data_max = Decimal(1)
        else:
            self._data_min = Decimal(domain_min)
            self._data_max = Decimal(domain_max)

        self._ticker = ScoreTicker(self._data_min, self._data_max)

    def contains(self, v):
        """
        Return :code:`True` if a given value is contained within this scale's
        domain.
        """
        return self._data_min <= v <= self._data_max

    def project(self, value, range_min, range_max):
        """
        Project a value in this scale's domain to a target range.
        """
        value = Decimal(value)
        range_min = Decimal(range_min)
        range_max = Decimal(range_max)

        pos = (value - self._ticker.min) / (self._ticker.max - self._ticker.min)

        return ((range_max - range_min) * pos) + range_min

    def project_interval(self, value, range_min, range_max):
        """
        Project a value in this scale's domain to an interval in the target
        range. This is used for places :class:`.Bars` and :class:`.Columns`.
        """
        raise NotImplementedError

    def ticks(self):
        """
        Generate a series of ticks for this scale.
        """
        return self._ticker.ticks
