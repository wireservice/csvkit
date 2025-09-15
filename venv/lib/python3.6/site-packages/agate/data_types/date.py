import locale
from datetime import date, datetime, time

import parsedatetime

from agate.data_types.base import DataType
from agate.exceptions import CastError

ZERO_DT = datetime.combine(date.min, time.min)


class Date(DataType):
    """
    Data representing dates alone.

    :param date_format:
        A formatting string for :meth:`datetime.datetime.strptime` to use
        instead of using regex-based parsing.
    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted dates.
    """
    def __init__(self, date_format=None, locale=None, **kwargs):
        super().__init__(**kwargs)

        self.date_format = date_format
        self.locale = locale

        self._constants = parsedatetime.Constants(localeID=self.locale)
        self._parser = parsedatetime.Calendar(constants=self._constants, version=parsedatetime.VERSION_CONTEXT_STYLE)

    def __getstate__(self):
        """
        Return state values to be pickled. Exclude _constants and _parser because parsedatetime
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
        Cast a single value to a :class:`datetime.date`.

        If both `date_format` and `locale` have been specified
        in the `agate.Date` instance, the `cast()` function
        is not thread-safe.
        :returns: :class:`datetime.date` or :code:`None`.
        """
        if type(d) is date or d is None:
            return d

        if isinstance(d, str):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as date.' % d)

        if self.date_format:
            orig_locale = None
            if self.locale:
                orig_locale = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, (self.locale, 'UTF-8'))

            try:
                dt = datetime.strptime(d, self.date_format)
            except (ValueError, TypeError):
                raise CastError('Value "%s" does not match date format.' % d)
            finally:
                if orig_locale:
                    locale.setlocale(locale.LC_TIME, orig_locale)

            return dt.date()

        try:
            (value, ctx, _, _, matched_text), = self._parser.nlp(d, sourceTime=ZERO_DT)
        except (TypeError, ValueError, OverflowError):
            raise CastError('Value "%s" does not match date format.' % d)
        else:
            if matched_text == d and ctx.hasDate and not ctx.hasTime:
                return value.date()

        raise CastError('Can not parse value "%s" as date.' % d)

    def csvify(self, d):
        if d is None:
            return None

        return d.isoformat()

    def jsonify(self, d):
        return self.csvify(d)
