def having(self, aggregations, test):
    """
    Create a new :class:`.TableSet` with only those tables that pass a test.

    This works by applying a sequence of :class:`Aggregation` instances to
    each table. The resulting dictionary of properties is then passed to
    the :code:`test` function.

    This method does not modify the underlying tables in any way.

    :param aggregations:
        A list of tuples in the format :code:`(name, aggregation)`, where
        each :code:`aggregation` is an instance of :class:`.Aggregation`.
    :param test:
        A function that takes a dictionary of aggregated properties and returns
        :code:`True` if it should be included in the new :class:`.TableSet`.
    :type test:
        :class:`function`
    :returns:
        A new :class:`.TableSet`.
    """
    new_tables = []
    new_keys = []

    for key, table in self.items():
        props = table.aggregate(aggregations)

        if test(props):
            new_tables.append(table)
            new_keys.append(key)

    return self._fork(new_tables, new_keys)
