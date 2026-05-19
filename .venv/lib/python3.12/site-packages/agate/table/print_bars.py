import sys
from collections import OrderedDict
from decimal import Decimal

from babel.numbers import format_decimal

from agate import config, utils
from agate.aggregations import Max, Min
from agate.data_types import Number
from agate.exceptions import DataTypeError


def print_bars(self, label_column_name='group', value_column_name='Count', domain=None, width=120, output=sys.stdout,
               printable=False):
    """
    Print a text-based bar chart based on this table.

    :param label_column_name:
        The column containing the label values. Defaults to :code:`group`, which
        is the default output of :meth:`.Table.pivot` or :meth:`.Table.bins`.
    :param value_column_name:
        The column containing the bar values. Defaults to :code:`Count`, which
        is the default output of :meth:`.Table.pivot` or :meth:`.Table.bins`.
    :param domain:
        A 2-tuple containing the minimum and maximum values for the chart's
        x-axis. The domain must be large enough to contain all values in
        the column.
    :param width:
        The width, in characters, to use for the bar chart. Defaults to
        :code:`120`.
    :param output:
        A file-like object to print to. Defaults to :code:`sys.stdout`.
    :param printable:
        If true, only printable characters will be outputed.
    """
    tick_mark = config.get_option('tick_char')
    horizontal_line = config.get_option('horizontal_line_char')
    locale = config.get_option('default_locale')

    if printable:
        bar_mark = config.get_option('printable_bar_char')
        zero_mark = config.get_option('printable_zero_line_char')
    else:
        bar_mark = config.get_option('bar_char')
        zero_mark = config.get_option('zero_line_char')

    y_label = label_column_name
    label_column = self._columns[label_column_name]

    # if not isinstance(label_column.data_type, Text):
    #     raise ValueError('Only Text data is supported for bar chart labels.')

    x_label = value_column_name
    value_column = self._columns[value_column_name]

    if not isinstance(value_column.data_type, Number):
        raise DataTypeError('Only Number data is supported for bar chart values.')

    output = output
    width = width

    # Format numbers
    decimal_places = utils.max_precision(value_column)
    value_formatter = utils.make_number_formatter(decimal_places)

    formatted_labels = []

    for label in label_column:
        formatted_labels.append(str(label))

    formatted_values = []
    for value in value_column:
        if value is None:
            formatted_values.append('-')
        else:
            formatted_values.append(format_decimal(
                value,
                format=value_formatter,
                locale=locale
            ))

    max_label_width = max(max([len(label) for label in formatted_labels]), len(y_label))
    max_value_width = max(max([len(value) for value in formatted_values]), len(x_label))

    plot_width = width - (max_label_width + max_value_width + 2)

    min_value = Min(value_column_name).run(self)
    max_value = Max(value_column_name).run(self)

    # Calculate dimensions
    if domain:
        x_min = Decimal(domain[0])
        x_max = Decimal(domain[1])

        if min_value < x_min or max_value > x_max:
            raise ValueError('Column contains values outside specified domain')
    else:
        x_min, x_max = utils.round_limits(min_value, max_value)

    # All positive
    if x_min >= 0:
        x_min = Decimal('0')
        plot_negative_width = 0
        zero_line = 0
        plot_positive_width = plot_width - 1
    # All negative
    elif x_max <= 0:
        x_max = Decimal('0')
        plot_negative_width = plot_width - 1
        zero_line = plot_width - 1
        plot_positive_width = 0
    # Mixed signs
    else:
        spread = x_max - x_min
        negative_portion = (x_min.copy_abs() / spread)

        # Subtract one for zero line
        plot_negative_width = int(((plot_width - 1) * negative_portion).to_integral_value())
        zero_line = plot_negative_width
        plot_positive_width = plot_width - (plot_negative_width + 1)

    def project(value):
        if value >= 0:
            return plot_negative_width + int((plot_positive_width * (value / x_max)).to_integral_value())
        return plot_negative_width - int((plot_negative_width * (value / x_min)).to_integral_value())

    # Calculate ticks
    ticks = OrderedDict()

    # First tick
    ticks[0] = x_min
    ticks[plot_width - 1] = x_max

    tick_fractions = [Decimal('0.25'), Decimal('0.5'), Decimal('0.75')]

    # All positive
    if x_min >= 0:
        for fraction in tick_fractions:
            value = x_max * fraction
            ticks[project(value)] = value
    # All negative
    elif x_max <= 0:
        for fraction in tick_fractions:
            value = x_min * fraction
            ticks[project(value)] = value
    # Mixed signs
    else:
        # Zero tick
        ticks[zero_line] = Decimal('0')

        # Halfway between min and 0
        value = x_min * Decimal('0.5')
        ticks[project(value)] = value

        # Halfway between 0 and max
        value = x_max * Decimal('0.5')
        ticks[project(value)] = value

    decimal_places = utils.max_precision(ticks.values())
    tick_formatter = utils.make_number_formatter(decimal_places)

    ticks_formatted = OrderedDict()

    for k, v in ticks.items():
        ticks_formatted[k] = format_decimal(
            v,
            format=tick_formatter,
            locale=locale
        )

    def write(line):
        output.write(line + '\n')

    # Chart top
    top_line = f'{y_label.ljust(max_label_width)} {x_label.rjust(max_value_width)}'
    write(top_line)

    # Bars
    for i, label in enumerate(formatted_labels):
        value = value_column[i]
        if value == 0 or value is None:
            bar_width = 0
        elif value > 0:
            bar_width = project(value) - plot_negative_width
        elif value < 0:
            bar_width = plot_negative_width - project(value)

        label_text = label.ljust(max_label_width)
        value_text = formatted_values[i].rjust(max_value_width)

        bar = bar_mark * bar_width

        if value is not None and value >= 0:
            gap = (' ' * plot_negative_width)

            # All positive
            if x_min <= 0:
                bar = gap + zero_mark + bar
            else:
                bar = bar + gap + zero_mark
        else:
            bar = ' ' * (plot_negative_width - bar_width) + bar

            # All negative or mixed signs
            if value is None or x_max > value:
                bar = bar + zero_mark

        bar = bar.ljust(plot_width)

        write(f'{label_text} {value_text} {bar}')

    # Axis & ticks
    axis = horizontal_line * plot_width
    tick_text = ' ' * width

    for i, (tick, label) in enumerate(ticks_formatted.items()):
        # First tick
        if tick == 0:
            offset = 0
        # Last tick
        elif tick == plot_width - 1:
            offset = -(len(label) - 1)
        else:
            offset = int(-(len(label) / 2))

        pos = (width - plot_width) + tick + offset

        # Don't print intermediate ticks that would overlap
        if tick != 0 and tick != plot_width - 1:
            if tick_text[pos - 1:pos + len(label) + 1] != ' ' * (len(label) + 2):
                continue

        tick_text = tick_text[:pos] + label + tick_text[pos + len(label):]
        axis = axis[:tick] + tick_mark + axis[tick + 1:]

    write(axis.rjust(width))
    write(tick_text)
