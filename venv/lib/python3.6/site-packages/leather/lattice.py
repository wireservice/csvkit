from leather.axis import Axis
from leather.chart import Chart
from leather.data_types import Date, DateTime
from leather.grid import Grid
from leather.scales import Linear, Scale, Temporal
from leather.series import Series
from leather.shapes import Line
from leather.utils import X, Y


class Lattice:
    """
    A grid of charts with synchronized shapes, scales, and axes.

    Lattice only supports graphing a single series of data.

    :param shape:
        An instance of :class:`.Shape` to use to render all series. Defaults
        to :class:`.Line` if not specified.
    """
    def __init__(self, shape=None):
        self._shape = shape or Line()
        self._series = []
        self._types = [None, None]
        self._scales = [None, None]
        self._axes = [None, None]

    def set_x_scale(self, scale):
        """
        Set the X :class:`.Scale` for this lattice.
        """
        self._scales[X] = scale

    def set_y_scale(self, scale):
        """
        See :meth:`.Lattice.set_x_scale`.
        """
        self._scales[Y] = scale

    def add_x_scale(self, domain_min, domain_max):
        """
        Create and add a :class:`.Scale`.

        If the provided domain values are :class:`date` or :class:`datetime`
        then a :class:`.Temporal` scale will be created, otherwise it will
        :class:`.Linear`.

        If you want to set a custom scale class use :meth:`.Lattice.set_x_scale`
        instead.
        """
        scale_type = Linear

        if isinstance(domain_min, Date.types) or isinstance(domain_min, DateTime.types):
            scale_type = Temporal

        self.set_x_scale(scale_type(domain_min, domain_max))

    def add_y_scale(self, domain_min, domain_max):
        """
        See :meth:`.Lattice.add_x_scale`.
        """
        scale_type = Linear

        if isinstance(domain_min, Date.types) or isinstance(domain_min, DateTime.types):
            scale_type = Temporal

        self.set_y_scale(scale_type(domain_min, domain_max))

    def set_x_axis(self, axis):
        """
        Set an :class:`.Axis` class for this lattice.
        """
        self._axes[X] = axis

    def set_y_axis(self, axis):
        """
        See :meth:`.Lattice.set_x_axis`.
        """
        self._axes[Y] = axis

    def add_x_axis(self, ticks=None, tick_formatter=None, name=None):
        """
        Create and add an X :class:`.Axis`.

        If you want to set a custom axis class use :meth:`.Lattice.set_x_axis`
        instead.
        """
        self._axes[X] = Axis(ticks=ticks, tick_formatter=tick_formatter, name=name)

    def add_y_axis(self, ticks=None, tick_formatter=None, name=None):
        """
        See :meth:`.Lattice.add_x_axis`.
        """
        self._axes[Y] = Axis(ticks=ticks, tick_formatter=tick_formatter, name=name)

    def add_one(self, data, x=None, y=None, title=None):
        """
        Add a data series to this lattice.

        :param data:
            A sequence of data suitable for constructing a :class:`.Series`,
            or a sequence of such objects.
        :param x:
            See :class:`.Series`.
        :param y:
            See :class:`.Series`.
        :param title:
            A title to render above this chart.
        """
        series = Series(data, x=x, y=y, name=title)

        for dimension in [X, Y]:
            if self._types[dimension]:
                if series._types[dimension] is not self._types[dimension]:
                    raise TypeError('All data series must have the same data types.')
            else:
                self._types[dimension] = series._types[dimension]

        self._shape.validate_series(series)
        self._series.append(series)

    def add_many(self, data, x=None, y=None, titles=None):
        """
        Same as :meth:`.Lattice.add_one` except :code:`data` is a list of data
        series to be added simultaneously.

        See :meth:`.Lattice.add_one` for other arguments.

        Note that :code:`titles` is a sequence of titles that must be the same
        length as :code:`data`.
        """
        for i, d in enumerate(data):
            title = titles[i] if titles else None

            self.add_one(d, x=x, y=y, title=title)

    def to_svg(self, path=None, width=None, height=None):
        """
        Render the lattice to an SVG.

        See :class:`.Grid` for additional documentation.
        """
        layers = [(s, self._shape) for s in self._series]

        if not self._scales[X]:
            self._scales[X] = Scale.infer(layers, X, self._types[X])

        if not self._scales[Y]:
            self._scales[Y] = Scale.infer(layers, Y, self._types[Y])

        if not self._axes[X]:
            self._axes[X] = Axis()

        if not self._axes[Y]:
            self._axes[Y] = Axis()

        grid = Grid()

        for i, series in enumerate(self._series):
            chart = Chart(title=series.name)
            chart.set_x_scale(self._scales[X])
            chart.set_y_scale(self._scales[Y])
            chart.set_x_axis(self._axes[X])
            chart.set_y_axis(self._axes[Y])
            chart.add_series(series, self._shape)

            grid.add_one(chart)

        return grid.to_svg(path, width, height)
