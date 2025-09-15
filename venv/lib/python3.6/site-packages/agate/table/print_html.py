import math
import sys

from babel.numbers import format_decimal

from agate import config, utils
from agate.data_types import Number, Text


def print_html(self, max_rows=20, max_columns=6, output=sys.stdout, max_column_width=20, locale=None, max_precision=3):
    """
    Print an HTML version of this table.

    :param max_rows:
        The maximum number of rows to display before truncating the data. This
        defaults to :code:`20` to prevent accidental printing of the entire
        table. Pass :code:`None` to disable the limit.
    :param max_columns:
        The maximum number of columns to display before truncating the data.
        This defaults to :code:`6` to prevent wrapping in most cases. Pass
        :code:`None` to disable the limit.
    :param output:
        A file-like object to print to. Defaults to :code:`sys.stdout`, unless
        running in Jupyter. (See above.)
    :param max_column_width:
        Truncate all columns to at most this width. The remainder will be
        replaced with ellipsis.
    :param locale:
        Provide a locale you would like to be used to format the output.
        By default it will use the system's setting.
    :max_precision:
        Puts a limit on the maximum precision displayed for number types.
        Numbers with lesser precision won't be affected.
        This defaults to :code:`3`. Pass :code:`None` to disable limit.
    """
    if max_rows is None:
        max_rows = len(self._rows)

    if max_columns is None:
        max_columns = len(self._columns)

    if max_precision is None:
        max_precision = float('inf')

    ellipsis = config.get_option('ellipsis_chars')
    truncation = config.get_option('text_truncation_chars')
    len_truncation = len(truncation)
    locale = locale or config.get_option('default_locale')

    rows_truncated = max_rows < len(self._rows)
    columns_truncated = max_columns < len(self._column_names)

    column_names = list(self._column_names[:max_columns])

    if columns_truncated:
        column_names.append(ellipsis)

    number_formatters = []
    formatted_data = []

    # Determine correct number of decimal places for each Number column
    for i, c in enumerate(self._columns):
        if i >= max_columns:
            break

        if isinstance(c.data_type, Number):
            max_places = utils.max_precision(c[:max_rows])
            add_ellipsis = False
            if max_places > max_precision:
                add_ellipsis = True
                max_places = max_precision
            number_formatters.append(utils.make_number_formatter(max_places, add_ellipsis))
        else:
            number_formatters.append(None)

    # Format data
    for i, row in enumerate(self._rows):
        if i >= max_rows:
            break

        formatted_row = []

        for j, v in enumerate(row):
            if j >= max_columns:
                v = ellipsis
            elif v is None:
                v = ''
            elif number_formatters[j] is not None and not math.isinf(v):
                v = format_decimal(
                    v,
                    format=number_formatters[j],
                    locale=locale
                )
            else:
                v = str(v)

            if max_column_width is not None and len(v) > max_column_width:
                v = '%s%s' % (v[:max_column_width - len_truncation], truncation)

            formatted_row.append(v)

            if j >= max_columns:
                break

        formatted_data.append(formatted_row)

    def write(line):
        output.write(line + '\n')

    def write_row(formatted_row):
        """
        Helper function that formats individual rows.
        """
        write('<tr>')

        for j, d in enumerate(formatted_row):
            # Text is left-justified, all other values are right-justified
            if isinstance(self._column_types[j], Text):
                write('<td style="text-align: left;">%s</td>' % d)
            else:
                write('<td style="text-align: right;">%s</td>' % d)

        write('</tr>')

    # Header
    write('<table>')
    write('<thead>')
    write('<tr>')

    for i, col in enumerate(column_names):
        write('<th>%s</th>' % col)

    write('</tr>')
    write('</thead>')
    write('<tbody>')

    # Rows
    for formatted_row in formatted_data:
        write_row(formatted_row)

    # Row indicating data was truncated
    if rows_truncated:
        write_row([ellipsis for n in column_names])

    # Footer
    write('</tbody>')
    write('</table>')
