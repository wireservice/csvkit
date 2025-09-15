import xml.etree.ElementTree as ET

from leather import theme


class Shape:
    """
    Base class for shapes that can be used to render data :class:`.Series`.
    """
    def validate_series(self, series):
        """
        Verify this shape can be used to render a given series.
        """
        raise NotImplementedError

    def to_svg(self, width, height, x_scale, y_scale, series, palette):
        """
        Render this shape to an SVG.
        """
        raise NotImplementedError

    def legend_to_svg(self, series, palette):
        """
        Render the legend entries for these shapes.
        """
        if hasattr(self, '_fill_color'):
            if self._fill_color:
                if callable(self._fill_color):
                    # TODO
                    fill_color = 'black'
                else:
                    fill_color = self._fill_color
            else:
                fill_color = next(palette)
        else:
            fill_color = None

        if hasattr(self, '_stroke_color'):
            if self._stroke_color:
                if callable(self._stroke_color):
                    # TODO
                    stroke_color = 'black'
                else:
                    stroke_color = self._stroke_color
            else:
                stroke_color = next(palette)
        else:
            stroke_color = None

        bubble_width = theme.legend_bubble_size + theme.legend_bubble_offset

        text = str(series.name) if series.name is not None else 'Unnamed series'
        text_width = (len(text) + 4) * theme.legend_font_char_width

        item_width = text_width + bubble_width

        # Group
        item_group = ET.Element('g')

        # Bubble
        bubble = ET.Element(
            'rect',
            x=str(0),
            y=str(-theme.legend_font_char_height + theme.legend_bubble_offset),
            width=str(theme.legend_bubble_size),
            height=str(theme.legend_bubble_size)
        )

        if fill_color:
            bubble.set('fill', fill_color)
        elif stroke_color:
            bubble.set('fill', stroke_color)

        item_group.append(bubble)

        # Label
        label = ET.Element(
            'text',
            x=str(bubble_width),
            y=str(0),
            fill=theme.legend_color
        )
        label.set('font-family', theme.legend_font_family)
        label.set('font-size', str(theme.legend_font_size))
        label.text = text

        item_group.append(label)

        return [(item_group, item_width)]


def style_function(datum):
    """
    This example shows how to define a function to specify style values for
    individual data points.

    :param datum:
        A :class:`.Datum` instance for the data row.
    """
    pass
