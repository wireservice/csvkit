from agate import utils
from agate.rows import Row
from agate.type_tester import TypeTester


def normalize(self, key, properties, property_column='property', value_column='value', column_types=None):
    """
    Create a new table with columns converted into rows values.

    For example:

    +---------+----------+--------+-------+
    |  name   | gender   | race   | age   |
    +=========+==========+========+=======+
    |  Jane   | female   | black  | 24    |
    +---------+----------+--------+-------+
    |  Jack   | male     | white  | 35    |
    +---------+----------+--------+-------+
    |  Joe    | male     | black  | 28    |
    +---------+----------+--------+-------+

    can be normalized on columns 'gender', 'race' and 'age':

    +---------+-----------+---------+
    |  name   | property  | value   |
    +=========+===========+=========+
    |  Jane   | gender    | female  |
    +---------+-----------+---------+
    |  Jane   | race      | black   |
    +---------+-----------+---------+
    |  Jane   | age       | 24      |
    +---------+-----------+---------+
    |  ...    |  ...      |  ...    |
    +---------+-----------+---------+

    This is the opposite of :meth:`.Table.denormalize`.

    :param key:
        A column name or a sequence of column names that should be
        maintained as they are in the normalized self. Typically these
        are the tables unique identifiers and any metadata about them.
    :param properties:
        A column name or a sequence of column names that should be
        converted to properties in the new self.
    :param property_column:
        The name to use for the column containing the property names.
    :param value_column:
        The name to use for the column containing the property values.
    :param column_types:
        A sequence of two column types for the property and value column in
        that order or an instance of :class:`.TypeTester`. Defaults to a
        generic :class:`.TypeTester`.
    :returns:
        A new :class:`.Table`.
    """
    from agate.table import Table

    new_rows = []

    if not utils.issequence(key):
        key = [key]

    if not utils.issequence(properties):
        properties = [properties]

    new_column_names = key + [property_column, value_column]

    row_names = []

    for row in self._rows:
        k = tuple(row[n] for n in key)
        left_row = list(k)

        if len(k) == 1:
            row_names.append(k[0])
        else:
            row_names.append(k)

        for f in properties:
            new_rows.append(Row((left_row + [f, row[f]]), new_column_names))

    key_column_types = [self._column_types[self._column_names.index(name)] for name in key]

    if column_types is None or isinstance(column_types, TypeTester):
        tester = TypeTester() if column_types is None else column_types
        force_update = dict(zip(key, key_column_types))
        force_update.update(tester._force)
        tester._force = force_update

        new_column_types = tester.run(new_rows, new_column_names)
    else:
        new_column_types = key_column_types + list(column_types)

    return Table(new_rows, new_column_names, new_column_types)
