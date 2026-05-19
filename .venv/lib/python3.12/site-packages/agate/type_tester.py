import warnings
from copy import copy

from agate.data_types.base import DEFAULT_NULL_VALUES
from agate.data_types.boolean import Boolean
from agate.data_types.date import Date
from agate.data_types.date_time import DateTime
from agate.data_types.number import Number
from agate.data_types.text import Text
from agate.data_types.time_delta import TimeDelta


class TypeTester:
    """
    Control how data types are inferred for columns in a given set of data.

    This class is used by passing it to the :code:`column_types` argument of
    the :class:`.Table` constructor, or the same argument for any other method
    that create a :class:`.Table`

    Type inference can be a slow process. To limit the number of rows of data to
    be tested, pass the :code:`limit` argument. Note that may cause errors if
    your data contains different types of values after the specified number of
    rows.

    By default, data types will be tested against each column in this order:

    1. :class:`.Boolean`
    2. :class:`.Number`
    3. :class:`.TimeDelta`
    #. :class:`.Date`
    #. :class:`.DateTime`
    #. :class:`.Text`

    Individual types may be specified using the :code:`force` argument. The type
    order by be changed, or entire types disabled, by using the :code:`types`
    argument. Beware that changing the order of the types may cause unexpected
    behavior.

    :param force:
        A dictionary where each key is a column name and each value is a
        :class:`.DataType` instance that overrides inference.
    :param limit:
        An optional limit on how many rows to evaluate before selecting the
        most likely type. Note that applying a limit may mean errors arise when
        the data is cast--if the guess is proved incorrect in further rows of
        data.
    :param types:
        A sequence of possible types to test against. This be used to specify
        what data formats you want to test against. For instance, you may want
        to exclude :class:`TimeDelta` from testing. It can also be used to pass
        options such as ``locale`` to :class:`.Number` or ``cast_nulls`` to
        :class:`.Text`. Take care in specifying the order of the list. It is
        the order they are tested in. :class:`.Text` should always be last.
    :param null_values:
        If :code:`types` is :code:`None`, a sequence of values which should be
        cast to :code:`None` when encountered by the default data types.
    """
    def __init__(self, force={}, limit=None, types=None, null_values=DEFAULT_NULL_VALUES):
        self._force = force
        self._limit = limit

        if types:
            self._possible_types = types
        else:
            # In order of preference
            self._possible_types = [
                Boolean(null_values=null_values),
                Number(null_values=null_values),
                TimeDelta(null_values=null_values),
                Date(null_values=null_values),
                DateTime(null_values=null_values),
                Text(null_values=null_values)
            ]

    def run(self, rows, column_names):
        """
        Apply type inference to the provided data and return an array of
        column types.

        :param rows:
            The data as a sequence of any sequences: tuples, lists, etc.
        """
        num_columns = len(column_names)
        hypotheses = [set(self._possible_types) for i in range(num_columns)]
        force_indices = []

        for name in self._force.keys():
            try:
                force_indices.append(column_names.index(name))
            except ValueError:
                warnings.warn('"%s" does not match the name of any column in this table.' % name, RuntimeWarning)

        if self._limit:
            sample_rows = rows[:self._limit]
        elif self._limit == 0:
            text = Text()
            return tuple([text] * num_columns)
        else:
            sample_rows = rows

        for row in sample_rows:
            for i in range(num_columns):
                if i in force_indices:
                    continue

                h = hypotheses[i]

                if len(h) == 1:
                    continue

                for column_type in copy(h):
                    if len(row) > i and not column_type.test(row[i]):
                        h.remove(column_type)

        column_types = []

        for i in range(num_columns):
            if i in force_indices:
                column_types.append(self._force[column_names[i]])
                continue

            h = hypotheses[i]

            # Select in prefer order
            for t in self._possible_types:
                if t in h:
                    column_types.append(t)
                    break

        return tuple(column_types)
