import xml.etree.ElementTree as ET

from leather.data_types import Number, Text
from leather.series import CategorySeries
from leather.shapes.base import Shape
from leather.utils import X, Y


class Bars(Shape):
    """
    Render a series of data as bars.

    :param fill_color:
        The color to fill the bars. You may also specify a
        :func:`.style_function`.
    """
    def __init__(self, fill_color=None):
        self._fill_color = fill_color

    def validate_series(self, series):
        """
        Verify this shape can be used to render a given series.
        """
        if isinstance(series, CategorySeries):
            raise ValueError('Bars can not be used to render CategorySeries.')

        if series.data_type(X) is not Number:
            raise ValueError('Bars only support Number values for the Y axis.')

        if series.data_type(Y) is not Text:
            raise ValueError('Bars only support Text values for the X axis.')

    def to_svg(self, width, height, x_scale, y_scale, series, palette):
        """
        Render bars to SVG elements.
        """
        group = ET.Element('g')
        group.set('class', 'series bars')

        zero_x = x_scale.project(0, 0, width)

        if self._fill_color:
            fill_color = self._fill_color
        else:
            fill_color = next(palette)

        for d in series.data():
            if d.x is None or d.y is None:
                continue

            y1, y2 = y_scale.project_interval(d.y, height, 0)
            proj_x = x_scale.project(d.x, 0, width)

            if d.x < 0:
                bar_x = proj_x
                bar_width = zero_x - proj_x
            else:
                bar_x = zero_x
                bar_width = proj_x - zero_x

            if callable(fill_color):
                color = fill_color(d)
            else:
                color = fill_color

            group.append(ET.Element(
                'rect',
                x=str(bar_x),
                y=str(y2),
                width=str(bar_width),
                height=str(y1 - y2),
                fill=color
            ))

        return group
