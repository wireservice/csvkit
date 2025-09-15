import leather


def column_chart(self, label=0, value=1, path=None, width=None, height=None):
    """
    Render a lattice/grid of column charts using :class:`leather.Lattice`.

    :param label:
        The name or index of a column to plot as the labels of the chart.
        Defaults to the first column in the table.
    :param value:
        The name or index of a column to plot as the values of the chart.
        Defaults to the second column in the table.
    :param path:
        If specified, the resulting SVG will be saved to this location. If
        :code:`None` and running in IPython, then the SVG will be rendered
        inline. Otherwise, the SVG data will be returned as a string.
    :param width:
        The width of the output SVG.
    :param height:
        The height of the output SVG.
    """
    if type(label) is int:
        label_name = self.column_names[label]
    else:
        label_name = label

    if type(value) is int:
        value_name = self.column_names[value]
    else:
        value_name = value

    chart = leather.Lattice(shape=leather.Columns())
    chart.add_x_axis(name=label_name)
    chart.add_y_axis(name=value_name)
    chart.add_many(self.values(), x=label, y=value, titles=self.keys())

    return chart.to_svg(path=path, width=width, height=height)
