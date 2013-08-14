#!/usr/bin/env python
try :
    from collections import Counter
except ImportError :
    from counterbackport import Counter
from copy import deepcopy
from itertools import groupby


def group_rows(column_names, rows, grouped_columns_ids, aggregations):
    """
    Given a list of rows (header row first), group by given column ids
    grouped_column_ids should be zero indexed
    """
    #Define key fn that makes tuple of given indices from row
    keyfn = lambda x: tuple(x[i] for i in grouped_columns_ids)

    yield list(keyfn(column_names)) + map(
        lambda a: a.get_column_name(column_names), aggregations)

    #Group
    for group, group_rows in groupby(rows, key=keyfn):
        aggregations_copy = deepcopy(aggregations)
        for row in group_rows:
            for agg in aggregations_copy:
                agg.take_row(row)
        yield list(group) + map(lambda a: a.get_result(), aggregations_copy)


class Aggregator(object):
    cast_type = None
    name_format = '%s'

    def __init__(self, column_id):
        self.column_id = column_id
        self.result = None

    def get_value(self, row):
        if self.cast_type:
            return self.cast_type(row[self.column_id])
        else:
            return row[self.column_id]

    def take_row(self, row):
        raise NotImplementedError()

    def get_result(self):
        return self.result

    def get_column_name(self, column_names):
        return self.name_format % column_names[self.column_id]


class CommonAggregator(Aggregator):
    """Returns most common value from column"""

    name_format = '%s'

    def __init__(self, column_id):
        super(CommonAggregator, self).__init__(column_id)
        self.counter = Counter()

    def take_row(self, row):
        self.counter[self.get_value(row)] += 1

    def get_result(self):
        return self.counter.most_common(1)[0][0]


class FunAggregator(Aggregator):
    cast_type = int
    name_format = '(%s)'
    fun = None

    def take_row(self, row):
        value = self.get_value(row)
        if self.result is not None:
            self.result = self.fun(value, self.result)
        else:
            self.result = value


class MaxAggregator(FunAggregator):
    name_format = 'max(%s)'
    fun = staticmethod(max)


class MinAggregator(FunAggregator):
    name_format = 'min(%s)'
    fun = staticmethod(min)


class SumAggregator(FunAggregator):
    name_format = 'sum(%s)'
    fun = staticmethod(lambda a, b: a + b)


class ConditionCountAggregator(Aggregator):
    def condition(self, value):
        return True

    def take_row(self, row):
        value = self.get_value(row)
        if self.result is not None:
            if self.condition(value):
                self.result += 1
        else:
            if self.condition(value):
                self.result = 1
            else:
                self.result = 0


class CountAggregator(ConditionCountAggregator):
    name_format = 'count(%s)'
    pass


class CountAAggregator(ConditionCountAggregator):
    name_format = 'countA(%s)'
    cast_type = int

    def condition(self, value):
        return value > 0


aggregate_functions = {
    'min': MinAggregator,
    'max': MaxAggregator,
    'sum': SumAggregator,
    'count': CountAggregator,
    'countA': CountAAggregator,
    'common': CommonAggregator,

}
