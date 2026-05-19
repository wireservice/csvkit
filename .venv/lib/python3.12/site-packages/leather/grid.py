import math
import os
import xml.etree.ElementTree as ET

import leather.svg as svg
from leather import theme
from leather.utils import IPythonSVG


class Grid:
    """
    A container for a set of :class:`.Chart` instances that are rendered in a
    grid layout.
    """
    def __init__(self):
        self._charts = []

    def add_one(self, chart):
        """
        Add a :class:`.Chart` to the grid.
        """
        self._charts.append(chart)

    def add_many(self, charts):
        """
        Add a sequence of charts to this grid.
        """
        self._charts.extend(charts)

    def to_svg(self, path=None, width=None, height=None):
        """
        Render the grid to an SVG.

        The :code:`width` and :code:`height` arguments refer to the size of the
        entire grid. The size of individual charts will be inferred
        automatically.

        See :meth:`.Chart.to_svg` for arguments.
        """
        if not width or not height:
            count = len(self._charts)

            columns = math.ceil(math.sqrt(count))
            rows = math.ceil(count / columns)

            width = columns * theme.default_chart_width
            height = rows * theme.default_chart_height

        root = ET.Element(
            'svg',
            width=str(width),
            height=str(height),
            version='1.1',
            xmlns='http://www.w3.org/2000/svg'
        )

        # Root /  background
        root_group = ET.Element('g')

        root_group.append(ET.Element(
            'rect',
            x=str(0),
            y=str(0),
            width=str(width),
            height=str(height),
            fill=theme.background_color
        ))

        root.append(root_group)

        # Charts
        grid_group = ET.Element('g')

        chart_count = len(self._charts)
        grid_width = math.ceil(math.sqrt(chart_count))
        grid_height = math.ceil(chart_count / grid_width)
        chart_width = width / grid_width
        chart_height = height / grid_height

        for i, chart in enumerate(self._charts):
            x = (i % grid_width) * chart_width
            y = math.floor(i / grid_width) * chart_height

            group = ET.Element('g')
            group.set('transform', svg.translate(x, y))

            chart = chart.to_svg_group(chart_width, chart_height)
            group.append(chart)

            grid_group.append(group)

        root_group.append(grid_group)

        svg_text = svg.stringify(root)
        close = True

        if path:
            f = None

            try:
                if hasattr(path, 'write'):
                    f = path
                    close = False
                else:
                    dirpath = os.path.dirname(path)

                    if dirpath and not os.path.exists(dirpath):
                        os.makedirs(dirpath)

                    f = open(path, 'w')

                f.write(svg.HEADER)
                f.write(svg_text)
            finally:
                if close and f is not None:
                    f.close()
        else:
            return IPythonSVG(svg_text)
