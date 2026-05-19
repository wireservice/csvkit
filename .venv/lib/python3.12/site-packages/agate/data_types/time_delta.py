import datetime

import pytimeparse

from agate.data_types.base import DataType
from agate.exceptions import CastError


class TimeDelta(DataType):
    """
    Data representing the interval between two dates and/or times.
    """
    def cast(self, d):
        """
        Cast a single value to :class:`datetime.timedelta`.

        :param d:
            A value to cast.
        :returns:
            :class:`datetime.timedelta` or :code:`None`
        """
        if isinstance(d, datetime.timedelta) or d is None:
            return d
        if isinstance(d, str):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as timedelta.' % d)

        try:
            seconds = pytimeparse.parse(d)
        except AttributeError:
            seconds = None

        if seconds is None:
            raise CastError('Can not parse value "%s" to as timedelta.' % d)

        return datetime.timedelta(seconds=seconds)
