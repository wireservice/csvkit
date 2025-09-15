from agate.exceptions import UnsupportedAggregationError


class Aggregation:  # pragma: no cover
    """
    Aggregations create a new value by summarizing a :class:`.Column`.

    Aggregations are applied with :meth:`.Table.aggregate` and
    :meth:`.TableSet.aggregate`.

    When creating a custom aggregation, ensure that the values returned by
    :meth:`.Aggregation.run` are of the type specified by
    :meth:`.Aggregation.get_aggregate_data_type`. This can be ensured by using
    the :meth:`.DataType.cast` method. See :class:`.Summary` for an example.
    """
    def __str__(self):
        """
        String representation of this column. May be used as a column name in
        generated tables.
        """
        return self.__class__.__name__

    def get_aggregate_data_type(self, table):
        """
        Get the data type that should be used when using this aggregation with
        a :class:`.TableSet` to produce a new column.

        Should raise :class:`.UnsupportedAggregationError` if this column does
        not support aggregation into a :class:`.TableSet`. (For example, if it
        does not return a single value.)
        """
        raise UnsupportedAggregationError()

    def validate(self, table):
        """
        Perform any checks necessary to verify this aggregation can run on the
        provided table without errors. This is called by
        :meth:`.Table.aggregate` before :meth:`run`.
        """
        pass

    def run(self, table):
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()
