from agate import utils
from agate.aggregations import Count


def pivot(self, key=None, pivot=None, aggregation=None, computation=None, default_value=utils.default, key_name=None):
    """
    Create a new table by grouping the data, aggregating those groups,
    applying a computation, and then organizing the groups into new rows and
    columns.

    This is sometimes called a "crosstab".

    +---------+---------+--------+
    |  name   |  race   | gender |
    +=========+=========+========+
    |  Joe    |  white  | male   |
    +---------+---------+--------+
    |  Jane   |  black  | female |
    +---------+---------+--------+
    |  Josh   |  black  | male   |
    +---------+---------+--------+
    |  Jim    |  asian  | female |
    +---------+---------+--------+

    This table can be pivoted with :code:`key` equal to "race" and
    :code:`columns` equal to "gender". The default aggregation is
    :class:`.Count`. This would result in the following table.

    +---------+---------+--------+
    |  race   |  male   | female |
    +=========+=========+========+
    |  white  |  1      | 0      |
    +---------+---------+--------+
    |  black  |  1      | 1      |
    +---------+---------+--------+
    |  asian  |  0      | 1      |
    +---------+---------+--------+

    If one or more keys are specified then the resulting table will
    automatically have :code:`row_names` set to those keys.

    See also the related method :meth:`.Table.denormalize`.

    :param key:
        Either the name of a column from the this table to group by, a
        sequence of such column names, a :class:`function` that takes a
        row and returns a value to group by, or :code:`None`, in which case
        there will be only a single row in the output table.
    :param pivot:
        A column name whose unique values will become columns in the new
        table, or :code:`None` in which case there will be a single value
        column in the output table.
    :param aggregation:
        An instance of an :class:`.Aggregation` to perform on each group of
        data in the pivot table. (Each cell is the result of an aggregation
        of the grouped data.)

        If not specified this defaults to :class:`.Count` with no arguments.
    :param computation:
        An optional :class:`.Computation` instance to be applied to the
        aggregated sequence of values before they are transposed into the
        pivot table.

        Use the class name of the aggregation as your column name argument
        when constructing your computation. (This is "Count" if using the
        default value for :code:`aggregation`.)
    :param default_value:
        Value to be used for missing values in the pivot table. Defaults to
        :code:`Decimal(0)`. If performing non-mathematical aggregations you
        may wish to set this to :code:`None`.
    :param key_name:
        A name for the key column in the output table. This is most
        useful when the provided key is a function. This argument is not
        valid when :code:`key` is a sequence.
    :returns:
        A new :class:`.Table`.
    """
    if key is None:
        key = []
    elif not utils.issequence(key):
        key = [key]
    elif key_name:
        raise ValueError('key_name is not a valid argument when key is a sequence.')

    if aggregation is None:
        aggregation = Count()

    groups = self

    for k in key:
        groups = groups.group_by(k, key_name=key_name)

    aggregation_name = str(aggregation)
    computation_name = str(computation) if computation else None

    def apply_computation(table):
        computed = table.compute([
            (computation_name, computation)
        ])

        excluded = computed.exclude([aggregation_name])

        return excluded

    if pivot is not None:
        groups = groups.group_by(pivot)

        column_type = aggregation.get_aggregate_data_type(self)

        table = groups.aggregate([
            (aggregation_name, aggregation)
        ])

        pivot_count = len(set(table.columns[pivot].values()))

        if computation is not None:
            column_types = computation.get_computed_data_type(table)
            table = apply_computation(table)

        column_types = [column_type] * pivot_count

        table = table.denormalize(key, pivot, computation_name or aggregation_name, default_value=default_value,
                                  column_types=column_types)
    else:
        table = groups.aggregate([
            (aggregation_name, aggregation)
        ])

        if computation:
            table = apply_computation(table)

    return table
