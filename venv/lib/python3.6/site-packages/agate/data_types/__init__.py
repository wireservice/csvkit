"""
Data types define how data should be imported during the creation of a
:class:`.Table`.

If column types are not explicitly specified when a :class:`.Table` is created,
agate will attempt to guess them. The :class:`.TypeTester` class can be used to
control how types are guessed.
"""

from agate.data_types.base import DEFAULT_NULL_VALUES, DataType
from agate.data_types.boolean import DEFAULT_FALSE_VALUES, DEFAULT_TRUE_VALUES, Boolean
from agate.data_types.date import Date
from agate.data_types.date_time import DateTime
from agate.data_types.number import Number
from agate.data_types.text import Text
from agate.data_types.time_delta import TimeDelta
from agate.exceptions import CastError
