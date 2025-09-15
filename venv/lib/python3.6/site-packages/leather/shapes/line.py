import xml.etree.ElementTree as ET

from leather import theme
from leather.data_types import Text
from leather.series import CategorySeries
from leather.shapes.base import Shape
from leather.utils import X, Y


class Line(Shape):
    """
    Render a series of data as a line.

    :param stroke_color:
        The color to stroke the lines. If not provided, default chart colors
        will be used.
    :param width:
        The width of the lines. Defaults to :data:`.theme.default_line_width`.
    """
    def __init__(self, stroke_color=None, width=None, stroke_dasharray=None):
        self._stroke_color = stroke_color
        self._width = width or theme.default_line_width
        self._stroke_dasharray = stroke_dasharray or theme.default_stroke_dasharray

    def validate_series(self, series):
        """
        Verify this shape can be used to render a given series.
        """
        if isinstance(series, CategorySeries):
            raise ValueError('Line can not be used to render CategorySeries.')

        if series.data_type(X) is Text or series.data_type(Y) is Text:
            raise ValueError('Line does not support Text values.')

    def _new_path(self, stroke_color):
        """
        Start a new path.
        """
        path = ET.Element(
            'path',
            stroke=stroke_color,
            fill='none'
        )
        path.set('stroke-width', str(self._width))
        if self._stroke_dasharray != 'none':
            path.set('stroke-dasharray', self._stroke_dasharray)

        return path

    def to_svg(self, width, height, x_scale, y_scale, series, palette):
        """
        Render lines to SVG elements.
        """
        group = ET.Element('g')
        group.set('class', 'series lines')

        if self._stroke_color:
            stroke_color = self._stroke_color
        else:
            stroke_color = next(palette)

        path = self._new_path(stroke_color)
        path_d = []

        for d in series.data():
            if d.x is None or d.y is None:
                if path_d:
                    path.set('d', ' '.join(path_d))
                    group.append(path)

                path_d = []
                path = self._new_path(stroke_color)

                continue

            proj_x = x_scale.project(d.x, 0, width)
            proj_y = y_scale.project(d.y, height, 0)

            if not path_d:
                command = 'M'
            else:
                command = 'L'

            path_d.extend([
                command,
                str(proj_x),
                str(proj_y)
            ])

        if path_d:
            path.set('d', ' '.join(path_d))
            group.append(path)

        return group
