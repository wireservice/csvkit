import datetime
import locale

import isodate
import parsedatetime

from agate.data_types.base import DataType
from agate.exceptions import CastError


class DateTime(DataType):
    """
    Data representing dates with times.

    :param datetime_format:
        A formatting string for :meth:`datetime.datetime.strptime` to use
        instead of using regex-based parsing.
    :param timezone:
        A ``ZoneInfo`` timezone to apply to each parsed date.
    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted datetimes.
    """
    def __init__(self, datetime_format=None, timezone=None, locale=None, **kwargs):
        super().__init__(**kwargs)

        self.datetime_format = datetime_format
        self.timezone = timezone
        self.locale = locale

        now = datetime.datetime.now()
        self._source_time = datetime.datetime(
            now.year, now.month, now.day, 0, 0, 0, 0, None
        )
        self._constants = parsedatetime.Constants(localeID=self.locale)
        self._parser = parsedatetime.Calendar(constants=self._constants, version=parsedatetime.VERSION_CONTEXT_STYLE)

    def __getstate__(self):
        """
        Return state values to be pickled. Exclude _parser because parsedatetime
        cannot be pickled.
        """
        odict = self.__dict__.copy()
        del odict['_constants']
        del odict['_parser']
        return odict

    def __setstate__(self, ndict):
        """
        Restore state from the unpickled state values. Set _constants to an instance
        of the parsedatetime Constants class, and _parser to an instance
        of the parsedatetime Calendar class.
        """
        self.__dict__.update(ndict)
        self._constants = parsedatetime.Constants(localeID=self.locale)
        self._parser = parsedatetime.Calendar(constants=self._constants, version=parsedatetime.VERSION_CONTEXT_STYLE)

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        If both `date_format` and `locale` have been specified
        in the `agate.DateTime` instance, the `cast()` function
        is not thread-safe.
        :returns: :class:`datetime.datetime` or :code:`None`.
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d
        if isinstance(d, datetime.date):
            return datetime.datetime.combine(d, datetime.time(0, 0, 0))
        if isinstance(d, str):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as datetime.' % d)

        if self.datetime_format:
            orig_locale = None
            if self.locale:
                orig_locale = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, (self.locale, 'UTF-8'))

            try:
                dt = datetime.datetime.strptime(d, self.datetime_format)
            except (ValueError, TypeError):
                raise CastError('Value "%s" does not match date format.' % d)
            finally:
                if orig_locale:
                    locale.setlocale(locale.LC_TIME, orig_locale)

            return dt

        try:
            (_, _, _, _, matched_text), = self._parser.nlp(d, sourceTime=self._source_time)
        except Exception:
            matched_text = None
        else:
            value, ctx = self._parser.parseDT(
                d,
                sourceTime=self._source_time,
                tzinfo=self.timezone
            )

            if matched_text == d and ctx.hasDate and ctx.hasTime:
                return value
            if matched_text == d and ctx.hasDate and not ctx.hasTime:
                return datetime.datetime.combine(value.date(), datetime.time.min)

        try:
            dt = isodate.parse_datetime(d)

            return dt
        except Exception:
            pass

        raise CastError('Can not parse value "%s" as datetime.' % d)

    def csvify(self, d):
        if d is None:
            return None

        return d.isoformat()

    def jsonify(self, d):
        return self.csvify(d)
