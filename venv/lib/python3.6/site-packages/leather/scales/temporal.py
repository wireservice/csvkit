from leather.scales.base import Scale
from leather.ticks.score_time import ScoreTimeTicker


class Temporal(Scale):
    """
    A scale that linearly maps date/datetime values from a domain to a range.

    :param domain_min:
        The minimum date/datetime of the input domain.
    :param domain_max:
        The maximum date/datetime of the input domain.
    """
    def __init__(self, domain_min, domain_max):
        if domain_min >= domain_max:
            raise ValueError(
                'Domain minimum must be less than domain maximum. '
                'Inverted domains are not currently supported.'
            )

        self._data_min = domain_min
        self._data_max = domain_max

        self._ticker = ScoreTimeTicker(self._data_min, self._data_max)

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

    def format_tick(self, value, i, count):
        """
        Format ticks for display.

        This method is used as a default which will be ignored if the user
        provides a custom tick formatter to the axis.
        """
        return self._ticker.format_tick(value)
