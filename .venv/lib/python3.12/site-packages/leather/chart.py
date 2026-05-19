import os
import warnings
import xml.etree.ElementTree as ET

import leather.svg as svg
from leather import theme
from leather.axis import Axis
from leather.data_types import Date, DateTime
from leather.scales import Linear, Scale, Temporal
from leather.series import CategorySeries, Series
from leather.shapes import Bars, Columns, Dots, Line
from leather.utils import DIMENSION_NAMES, Box, IPythonSVG, X, Y


class Chart:
    """
    Container for all chart types.

    :param title:
        An optional title that will be rendered at the top of the chart.
    """
    def __init__(self, title=None):
        self._title = title
        self._series_colors = theme.default_series_colors

        self._layers = []
        self._types = [None, None]
        self._scales = [None, None]
        self._axes = [None, None]

    def _palette(self):
        """
        Return a generator for series colors.
        """
        return (color for color in self._series_colors)

    def set_x_scale(self, scale):
        """
        Set the X :class:`.Scale` for this chart.
        """
        self._scales[X] = scale

    def set_y_scale(self, scale):
        """
        See :meth:`.Chart.set_x_scale`.
        """
        self._scales[Y] = scale

    def add_x_scale(self, domain_min, domain_max):
        """
        Create and add a :class:`.Scale`.

        If the provided domain values are :class:`date` or :class:`datetime`
        then a :class:`.Temporal` scale will be created, otherwise it will
        :class:`.Linear`.

        If you want to set a custom scale class use :meth:`.Chart.set_x_scale`
        instead.
        """
        scale_type = Linear

        if isinstance(domain_min, Date.types) or isinstance(domain_min, DateTime.types):
            scale_type = Temporal

        self.set_x_scale(scale_type(domain_min, domain_max))

    def add_y_scale(self, domain_min, domain_max):
        """
        See :meth:`.Chart.add_x_scale`.
        """
        scale_type = Linear

        if isinstance(domain_min, Date.types) or isinstance(domain_min, DateTime.types):
            scale_type = Temporal

        self.set_y_scale(scale_type(domain_min, domain_max))

    def set_x_axis(self, axis):
        """
        Set an :class:`.Axis` class for this chart.
        """
        self._axes[X] = axis

    def set_y_axis(self, axis):
        """
        See :meth:`.Chart.set_x_axis`.
        """
        self._axes[Y] = axis

    def add_x_axis(self, ticks=None, tick_formatter=None, name=None):
        """
        Create and add an X :class:`.Axis`.

        If you want to set a custom axis class use :meth:`.Chart.set_x_axis`
        instead.
        """
        self._axes[X] = Axis(ticks, tick_formatter, name)

    def add_y_axis(self, ticks=None, tick_formatter=None, name=None):
        """
        See :meth:`.Chart.add_x_axis`.
        """
        self._axes[Y] = Axis(ticks, tick_formatter, name)

    def add_series(self, series, shape):
        """
        Add a data :class:`.Series` to the chart. The data types of the new
        series must be consistent with any series that have already been added.

        There are several shortcuts for adding different types of data series.
        See :meth:`.Chart.add_bars`, :meth:`.Chart.add_columns`,
        :meth:`.Chart.add_dots`, and :meth:`.Chart.add_line`.
        """
        if self._layers and isinstance(self._layers[0][0], CategorySeries):
            raise RuntimeError('Additional series can not be added to a chart with a CategorySeries.')

        if isinstance(series, CategorySeries):
            self._types = series._types
        else:
            for dim in [X, Y]:
                if not self._types[dim]:
                    self._types[dim] = series._types[dim]
                elif series._types[dim] is not self._types[dim]:
                    raise TypeError(f'Can\'t mix axis-data types: {series._types[dim]} and {self._types[dim]}')

        shape.validate_series(series)

        self._layers.append((
            series,
            shape
        ))

    def add_bars(self, data, x=None, y=None, name=None, fill_color=None):
        """
        Create and add a :class:`.Series` rendered with :class:`.Bars`.

        Note that when creating bars in this way the order of the series data
        will be reversed so that the first item in the series is displayed
        as the top-most bar in the graphic. If you don't want this to happen
        use :meth:`.Chart.add_series` instead.
        """
        self.add_series(
            Series(list(reversed(data)), x=x, y=y, name=name),
            Bars(fill_color)
        )

    def add_columns(self, data, x=None, y=None, name=None, fill_color=None):
        """
        Create and add a :class:`.Series` rendered with :class:`.Columns`.
        """
        self.add_series(
            Series(data, x=x, y=y, name=name),
            Columns(fill_color)
        )

    def add_dots(self, data, x=None, y=None, name=None, fill_color=None, radius=None):
        """
        Create and add a :class:`.Series` rendered with :class:`.Dots`.
        """
        self.add_series(
            Series(data, x=x, y=y, name=name),
            Dots(fill_color, radius)
        )

    def add_line(self, data, x=None, y=None, name=None, stroke_color=None, width=None, stroke_dasharray=None):
        """
        Create and add a :class:`.Series` rendered with :class:`.Line`.
        """
        self.add_series(
            Series(data, x=x, y=y, name=name),
            Line(stroke_color, width, stroke_dasharray)
        )

    def _validate_dimension(self, dimension):
        """
        Validates that the given scale and axis are valid for the data that
        has been added to this chart. If a scale or axis has not been set,
        generates automated ones.
        """
        scale = self._scales[dimension]
        axis = self._axes[dimension]

        if not scale:
            scale = Scale.infer(self._layers, dimension, self._types[dimension])
        else:
            for series, shape in self._layers:
                if not scale.contains(series.min(dimension)) or not scale.contains(series.max(dimension)):
                    d = DIMENSION_NAMES[dimension]
                    warnings.warn(
                        'Data contains values outside %s scale domain. '
                        'All data points may not be visible on the chart.' % d
                    )

                    # Only display once per axis
                    break

        if not axis:
            axis = Axis()

        return (scale, axis)

    def to_svg_group(self, width=None, height=None):
        """
        Render this chart to an SVG group element.

        This can then be placed inside an :code:`<svg>` tag to make a complete
        SVG graphic.

        See :meth:`.Chart.to_svg` for arguments.
        """
        width = width or theme.default_width
        height = height or theme.default_height

        if not self._layers:
            raise ValueError('You must add at least one series to the chart before rendering.')

        if isinstance(theme.margin, float):
            default_margin = width * theme.margin

            margin = Box(
                top=default_margin,
                right=default_margin,
                bottom=default_margin,
                left=default_margin
            )
        elif isinstance(margin, int):
            margin = Box(margin, margin, margin, margin)
        elif not isinstance(margin, Box):
            margin = Box(*margin)

        # Root / background
        root_group = ET.Element('g')

        root_group.append(ET.Element(
            'rect',
            x=str(0),
            y=str(0),
            width=str(width),
            height=str(height),
            fill=theme.background_color
        ))

        # Margins
        margin_group = ET.Element('g')
        margin_group.set('transform', svg.translate(margin.left, margin.top))

        margin_width = width - (margin.left + margin.right)
        margin_height = height - (margin.top + margin.bottom)

        root_group.append(margin_group)

        # Header
        header_group = ET.Element('g')

        header_margin = 0

        if self._title:
            label = ET.Element(
                'text',
                x=str(0),
                y=str(0),
                fill=theme.title_color
            )
            label.set('font-family', theme.title_font_family)
            label.set('font-size', str(theme.title_font_size))
            label.text = str(self._title)

            header_group.append(label)
            header_margin += theme.title_font_char_height + theme.title_gap

        # Legend
        if len(self._layers) > 1 or isinstance(self._layers[0][0], CategorySeries):
            legend_group = ET.Element('g')
            legend_group.set('transform', svg.translate(0, header_margin))

            indent = 0
            rows = 1
            palette = self._palette()

            for series, shape in self._layers:
                for item_group, item_width in shape.legend_to_svg(series, palette):
                    if indent + item_width > width:
                        indent = 0
                        rows += 1

                    y = (rows - 1) * (theme.legend_font_char_height + theme.legend_gap)
                    item_group.set('transform', svg.translate(indent, y))

                    indent += item_width

                    legend_group.append(item_group)

            legend_height = rows * (theme.legend_font_char_height + theme.legend_gap)

            header_margin += legend_height
            header_group.append(legend_group)

        margin_group.append(header_group)

        # Body
        body_group = ET.Element('g')
        body_group.set('transform', svg.translate(0, header_margin))

        body_width = margin_width
        body_height = margin_height - header_margin

        margin_group.append(body_group)

        # Axes
        x_scale, x_axis = self._validate_dimension(X)
        y_scale, y_axis = self._validate_dimension(Y)

        bottom_margin = x_axis.estimate_label_margin(x_scale, 'bottom')
        left_margin = y_axis.estimate_label_margin(y_scale, 'left')

        canvas_width = body_width - left_margin
        canvas_height = body_height - bottom_margin

        axes_group = ET.Element('g')
        axes_group.set('transform', svg.translate(left_margin, 0))

        axes_group.append(x_axis.to_svg(canvas_width, canvas_height, x_scale, 'bottom'))
        axes_group.append(y_axis.to_svg(canvas_width, canvas_height, y_scale, 'left'))

        header_group.set('transform', svg.translate(left_margin, 0))

        body_group.append(axes_group)

        # Series
        series_group = ET.Element('g')

        palette = self._palette()

        for series, shape in self._layers:
            series_group.append(shape.to_svg(canvas_width, canvas_height, x_scale, y_scale, series, palette))

        axes_group.append(series_group)

        return root_group

    def to_svg(self, path=None, width=None, height=None):
        """
        Render this chart to an SVG document.

        The :code:`width` and :code:`height` are specified in SVG's
        "unitless" units, however, it is usually convenient to specify them
        as though they were pixels.

        :param path:
            Filepath or file-like object to write to. If omitted then the SVG
            will be returned as a string. If running within IPython, then this
            will return a SVG object to be displayed.
        :param width:
            The output width, in SVG user units. Defaults to
            :data:`.theme.default_chart_width`.
        :param height:
            The output height, in SVG user units. Defaults to
            :data:`.theme.default_chart_height`.
        """
        width = width or theme.default_chart_width
        height = height or theme.default_chart_height

        root = ET.Element(
            'svg',
            width=str(width),
            height=str(height),
            version='1.1',
            xmlns='http://www.w3.org/2000/svg'
        )

        group = self.to_svg_group(width, height)
        root.append(group)

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
