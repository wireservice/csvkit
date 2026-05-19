from collections import OrderedDict

from agate import utils


def aggregate(self, aggregations):
    """
    Apply one or more :class:`.Aggregation` instances to this table.

    :param aggregations:
        A single :class:`.Aggregation` instance or a sequence of tuples in the
        format :code:`(name, aggregation)`, where each :code:`aggregation` is
        an instance of :class:`.Aggregation`.
    :returns:
        If the input was a single :class:`Aggregation` then a single result
        will be returned. If it was a sequence then an :class:`.OrderedDict` of
        results will be returned.
    """
    if utils.issequence(aggregations):
        results = OrderedDict()

        for name, agg in aggregations:
            agg.validate(self)

        for name, agg in aggregations:
            results[name] = agg.run(self)

        return results

    aggregations.validate(self)

    return aggregations.run(self)
