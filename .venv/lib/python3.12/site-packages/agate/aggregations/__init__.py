"""
Aggregations create a new value by summarizing a :class:`.Column`. For
example, :class:`.Mean`, when applied to a column containing :class:`.Number`
data, returns a single :class:`decimal.Decimal` value which is the average of
all values in that column.

Aggregations can be applied to single columns using the :meth:`.Table.aggregate`
method. The result is a single value if a one aggregation was applied, or
a tuple of values if a sequence of aggregations was applied.

Aggregations can be applied to instances of :class:`.TableSet` using the
:meth:`.TableSet.aggregate` method. The result is a new :class:`.Table`
with a column for each aggregation and a row for each table in the set.
"""

from agate.aggregations.all import All
from agate.aggregations.any import Any
from agate.aggregations.base import Aggregation
from agate.aggregations.count import Count
from agate.aggregations.deciles import Deciles
from agate.aggregations.first import First
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.iqr import IQR
from agate.aggregations.mad import MAD
from agate.aggregations.max import Max
from agate.aggregations.max_length import MaxLength
from agate.aggregations.max_precision import MaxPrecision
from agate.aggregations.mean import Mean
from agate.aggregations.median import Median
from agate.aggregations.min import Min
from agate.aggregations.mode import Mode
from agate.aggregations.percentiles import Percentiles
from agate.aggregations.quartiles import Quartiles
from agate.aggregations.quintiles import Quintiles
from agate.aggregations.stdev import PopulationStDev, StDev
from agate.aggregations.sum import Sum
from agate.aggregations.summary import Summary
from agate.aggregations.variance import PopulationVariance, Variance
