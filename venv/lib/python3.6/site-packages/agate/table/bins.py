from decimal import Decimal

from babel.numbers import format_decimal

from agate import utils
from agate.aggregations import Max, Min


def bins(self, column_name, count=10, start=None, end=None):
    """
    Generates (approximately) evenly sized bins for the values in a column.
    Bins may not be perfectly even if the spread of the data does not divide
    evenly, but all values will always be included in some bin.

    The resulting table will have two columns. The first will have
    the same name as the specified column, but will be type :class:`.Text`.
    The second will be named :code:`count` and will be of type
    :class:`.Number`.

    :param column_name:
        The name of the column to bin. Must be of type :class:`.Number`
    :param count:
        The number of bins to create. If not specified then each value will
        be counted as its own bin.
    :param start:
        The minimum value to start the bins at. If not specified the
        minimum value in the column will be used.
    :param end:
        The maximum value to end the bins at. If not specified the maximum
        value in the column will be used.
    :returns:
        A new :class:`Table`.
    """
    minimum, maximum = utils.round_limits(
        Min(column_name).run(self),
        Max(column_name).run(self)
    )
    # Infer bin start/end positions
    start = minimum if not start else Decimal(start)
    end = maximum if not end else Decimal(end)

    # Calculate bin size
    spread = abs(end - start)
    size = spread / count

    breaks = [start]

    # Calculate breakpoints
    for i in range(1, count + 1):
        top = start + (size * i)

        breaks.append(top)

    # Format bin names
    decimal_places = utils.max_precision(breaks)
    break_formatter = utils.make_number_formatter(decimal_places)

    def name_bin(i, j, first_exclusive=True, last_exclusive=False):
        inclusive = format_decimal(i, format=break_formatter)
        exclusive = format_decimal(j, format=break_formatter)

        output = '[' if first_exclusive else '('
        output += f'{inclusive} - {exclusive}'
        output += ']' if last_exclusive else ')'

        return output

    # Generate bins
    bin_names = []

    for i in range(1, len(breaks)):
        last_exclusive = (i == len(breaks) - 1)

        if i == 1 and minimum < start:
            name = name_bin(minimum, breaks[i], last_exclusive=last_exclusive)
        elif i == len(breaks) - 1 and maximum > end:
            name = name_bin(breaks[i - 1], maximum, last_exclusive=last_exclusive)
        else:
            name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

        bin_names.append(name)

    bin_names.append(None)

    # Lambda method for actually assigning values to bins
    def binner(row):
        value = row[column_name]

        if value is None:
            return None

        i = 1

        try:
            while value >= breaks[i]:
                i += 1
        except IndexError:
            i -= 1

        return bin_names[i - 1]

    # Pivot by lambda
    table = self.pivot(binner, key_name=column_name)

    # Sort by bin order
    return table.order_by(lambda r: bin_names.index(r[column_name]))
