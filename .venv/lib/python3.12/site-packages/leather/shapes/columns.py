import xml.etree.ElementTree as ET

from leather.data_types import Number, Text
from leather.series import CategorySeries
from leather.shapes.base import Shape
from leather.utils import X, Y


class Columns(Shape):
    """
    Render a series of data as columns.

    :param fill_color:
        The color to fill the columns. You may also specify a
        :func:`.style_function`.
    """
    def __init__(self, fill_color=None):
        self._fill_color = fill_color

    def validate_series(self, series):
        """
        Verify this shape can be used to render a given series.
        """
        if isinstance(series, CategorySeries):
            raise ValueError('Columns can not be used to render CategorySeries.')

        if series.data_type(X) is not Text:
            raise ValueError('Bars only support Text values for the X axis.')

        if series.data_type(Y) is not Number:
            raise ValueError('Bars only support Number values for the Y axis.')

    def to_svg(self, width, height, x_scale, y_scale, series, palette):
        """
        Render columns to SVG elements.
        """
        group = ET.Element('g')
        group.set('class', 'series columns')

        zero_y = y_scale.project(0, height, 0)

        if self._fill_color:
            fill_color = self._fill_color
        else:
            fill_color = next(palette)

        for d in series.data():
            if d.x is None or d.y is None:
                continue

            x1, x2 = x_scale.project_interval(d.x, 0, width)
            proj_y = y_scale.project(d.y, height, 0)

            if d.y < 0:
                column_y = zero_y
                column_height = proj_y - zero_y
            else:
                column_y = proj_y
                column_height = zero_y - proj_y

            if callable(fill_color):
                color = fill_color(d)
            else:
                color = fill_color

            group.append(ET.Element(
                'rect',
                x=str(x1),
                y=str(column_y),
                width=str(x2 - x1),
                height=str(column_height),
                fill=color
            ))

        return group
