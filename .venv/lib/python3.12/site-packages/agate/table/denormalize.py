from collections import OrderedDict
from decimal import Decimal

from agate import utils
from agate.data_types import Number
from agate.rows import Row
from agate.type_tester import TypeTester


def denormalize(self, key=None, property_column='property', value_column='value', default_value=utils.default,
                column_types=None):
    """
    Create a new table with row values converted into columns.

    For example:

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

    Can be denormalized so that each unique value in `field` becomes a
    column with `value` used for its values.

    +---------+----------+--------+-------+
    |  name   | gender   | race   | age   |
    +=========+==========+========+=======+
    |  Jane   | female   | black  | 24    |
    +---------+----------+--------+-------+
    |  Jack   | male     | white  | 35    |
    +---------+----------+--------+-------+
    |  Joe    | male     | black  | 28    |
    +---------+----------+--------+-------+

    If one or more keys are specified then the resulting table will
    automatically have :code:`row_names` set to those keys.

    This is the opposite of :meth:`.Table.normalize`.

    :param key:
        A column name or a sequence of column names that should be
        maintained as they are in the normalized table. Typically these
        are the tables unique identifiers and any metadata about them. Or,
        :code:`None` if there are no key columns.
    :param field_column:
        The column whose values should become column names in the new table.
    :param property_column:
        The column whose values should become the values of the property
        columns in the new table.
    :param default_value:
        Value to be used for missing values in the pivot table. If not
        specified :code:`Decimal(0)` will be used for aggregations that
        return :class:`.Number` data and :code:`None` will be used for
        all others.
    :param column_types:
        A sequence of column types with length equal to number of unique
        values in field_column or an instance of :class:`.TypeTester`.
        Defaults to a generic :class:`.TypeTester`.
    :returns:
        A new :class:`.Table`.
    """
    from agate.table import Table

    if key is None:
        key = []
    elif not utils.issequence(key):
        key = [key]

    field_names = []
    row_data = OrderedDict()

    for row in self.rows:
        row_key = tuple(row[k] for k in key)

        if row_key not in row_data:
            row_data[row_key] = OrderedDict()

        f = str(row[property_column])
        v = row[value_column]

        if f not in field_names:
            field_names.append(f)

        row_data[row_key][f] = v

    if default_value == utils.default:
        if isinstance(self.columns[value_column].data_type, Number):
            default_value = Decimal(0)
        else:
            default_value = None

    new_column_names = key + field_names

    new_rows = []
    row_names = []

    for k, v in row_data.items():
        row = list(k)

        if len(k) == 1:
            row_names.append(k[0])
        else:
            row_names.append(k)

        for f in field_names:
            if f in v:
                row.append(v[f])
            else:
                row.append(default_value)

        new_rows.append(Row(row, new_column_names))

    key_column_types = [self.column_types[self.column_names.index(name)] for name in key]

    if column_types is None or isinstance(column_types, TypeTester):
        tester = TypeTester() if column_types is None else column_types
        force_update = dict(zip(key, key_column_types))
        force_update.update(tester._force)
        tester._force = force_update

        new_column_types = tester.run(new_rows, new_column_names)
    else:
        new_column_types = key_column_types + list(column_types)

    return Table(new_rows, new_column_names, new_column_types, row_names=row_names)
