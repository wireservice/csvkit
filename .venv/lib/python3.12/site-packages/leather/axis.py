import xml.etree.ElementTree as ET

from leather import svg, theme


class Axis:
    """
    A horizontal or vertical chart axis.

    :param ticks:
        Instead of inferring tick values from the data, use exactly this
        sequence of ticks values. These will still be passed to the
        :code:`tick_formatter`.
    :param tick_formatter:
        An optional :func:`.tick_format_function`.
    """
    def __init__(self, ticks=None, tick_formatter=None, name=None):
        self._ticks = ticks
        self._tick_formatter = tick_formatter
        self._name = str(name) if name is not None else None

    def _estimate_left_tick_width(self, scale):
        """
        Estimate the y axis space used by tick labels.
        """
        tick_values = self._ticks or scale.ticks()
        tick_count = len(tick_values)
        tick_formatter = self._tick_formatter or scale.format_tick
        max_len = 0

        for i, value in enumerate(tick_values):
            max_len = max(max_len, len(tick_formatter(value, i, tick_count)))

        return max_len * theme.tick_font_char_width

    def estimate_label_margin(self, scale, orient):
        """
        Estimate the space needed for the tick labels.
        """
        margin = 0

        if orient == 'left':
            margin += self._estimate_left_tick_width(scale) + (theme.tick_size * 2)
        elif orient == 'bottom':
            margin += theme.tick_font_char_height + (theme.tick_size * 2)

        if self._name:
            margin += theme.axis_title_font_char_height + theme.axis_title_gap

        return margin

    def to_svg(self, width, height, scale, orient):
        """
        Render this axis to SVG elements.
        """
        group = ET.Element('g')
        group.set('class', 'axis ' + orient)

        # Axis title
        if self._name is not None:
            if orient == 'left':
                title_x = -(self._estimate_left_tick_width(scale) + theme.axis_title_gap)
                title_y = height / 2
                dy = ''
                transform = svg.rotate(270, title_x, title_y)
            elif orient == 'bottom':
                title_x = width / 2
                title_y = height + theme.tick_font_char_height + (theme.tick_size * 2) + theme.axis_title_gap
                dy = '1em'
                transform = ''

            title = ET.Element(
                'text',
                x=str(title_x),
                y=str(title_y),
                dy=dy,
                fill=theme.axis_title_color,
                transform=transform
            )
            title.set('text-anchor', 'middle')
            title.set('font-family', theme.axis_title_font_family)
            title.set('font-size', str(theme.axis_title_font_size))
            title.text = self._name

            group.append(title)

        # Ticks
        if orient == 'left':
            label_x = -(theme.tick_size * 2)
            x1 = -theme.tick_size
            x2 = width
            range_min = height
            range_max = 0
        elif orient == 'bottom':
            label_y = height + (theme.tick_size * 2)
            y1 = 0
            y2 = height + theme.tick_size
            range_min = 0
            range_max = width

        tick_values = self._ticks or scale.ticks()
        tick_count = len(tick_values)
        tick_formatter = self._tick_formatter or scale.format_tick

        zero_tick_group = None

        for i, value in enumerate(tick_values):
            # Tick group
            tick_group = ET.Element('g')
            tick_group.set('class', 'tick')

            if value == 0:
                zero_tick_group = tick_group
            else:
                group.append(tick_group)

            # Tick line
            projected_value = scale.project(value, range_min, range_max)

            if value == 0:
                tick_color = theme.zero_color
            else:
                tick_color = theme.tick_color

            if orient == 'left':
                y1 = projected_value
                y2 = projected_value

            elif orient == 'bottom':
                x1 = projected_value
                x2 = projected_value

            tick = ET.Element(
                'line',
                x1=str(x1),
                y1=str(y1),
                x2=str(x2),
                y2=str(y2),
                stroke=tick_color
            )
            tick.set('stroke-width', str(theme.tick_width))

            tick_group.append(tick)

            # Tick label
            if orient == 'left':
                x = label_x
                y = projected_value
                dy = '0.32em'
                text_anchor = 'end'
            elif orient == 'bottom':
                x = projected_value
                y = label_y
                dy = '1em'
                text_anchor = 'middle'

            label = ET.Element(
                'text',
                x=str(x),
                y=str(y),
                dy=dy,
                fill=theme.label_color
            )
            label.set('text-anchor', text_anchor)
            label.set('font-family', theme.tick_font_family)
            label.set('font-size', str(theme.tick_font_size))

            value = tick_formatter(value, i, tick_count)
            label.text = str(value)

            tick_group.append(label)

        if zero_tick_group is not None:
            group.append(zero_tick_group)

        return group


def tick_format_function(value, index, tick_count):
    """
    This example shows how to define a function to format tick values for
    display.

    :param x:
        The value to be formatted.
    :param index:
        The index of the tick.
    :param tick_count:
        The total number of ticks being displayed.
    :returns:
        A stringified tick value for display.
    """
    return str(value)
