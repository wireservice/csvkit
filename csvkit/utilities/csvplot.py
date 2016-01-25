#!/usr/bin/env python
# TODO: Add plot options
# TODO: Add styles

from csvkit import table
from csvkit.cli import CSVKitUtility
import os.path


try:
    import pygal
except ImportError:
    raise ImportError(
        'You need to install pygal to use csvplot. Try:\n\n    pip install pygal\n')

# supported charts
CHARTS = ['Line', 'StackedLine', 'Bar', 'StackedBar', 'XY']


class CSVPlot(CSVKitUtility):
    description = 'Plots columns from a csv file'

    def add_arguments(self):
        self.argparser.add_argument('-x', '--x', dest='xcol', default='-1',
                                    help='Column name or index to be used as x axis')
        self.argparser.add_argument('-c', '--columns', dest='ycol', default='-1',
                                    help=('Column names or indexes to be used as y axis (0 based). You can use a range 1-3 or comma separated column values 1,3,5. Non-numeric columns are automatically skipped (default: all)'))
        self.argparser.add_argument('--title', dest='title', default='',
                                    help='The title of the chart')
        self.argparser.add_argument('--type', dest='type', default='Line',
                                    choices=CHARTS,
                                    help='Kind of chart to generate')
        self.argparser.add_argument('--output', '-o', dest='output', default='browser',
                                    help='What kind output. default(browser)')

    def main(self):
        # get data
        tab = table.Table.from_csv(
            self.input_file,
            no_header_row=self.args.no_header_row,
            **self.reader_kwargs
        )
        header = tab.headers()
        ignored_columns = set()
        ############################################################
        #                   Parse input parameters                 #
        ############################################################
        # get x values if given
        x = None
        xcol = self.args.xcol
        if xcol != '-1':
            idx = header.index(xcol) if not xcol.isdigit() else int(xcol)
            x = tab[idx]
            ignored_columns.update([x.name])

        # get columns to be plotted
        ycol = self.args.ycol
        if ycol == '-1':
            columns = header
        elif ',' in ycol:                             # several columns
            columns = self.args.ycol.split(',')
        elif '-' in ycol:                             # range of columns
            start_col = int(ycol.split('-')[0])
            end_col = int(ycol.split('-')[-1])
            columns = map(str, range(start_col, end_col + 1))
        else:                                         # single column
            columns = [ycol]

        # find columns indexes excluding x
        col_idxs = [header.index(col) if not col.isdigit() else int(col)
                    for col in columns
                    if col not in ignored_columns]

        series = [tab[idx] for idx in col_idxs]

        # plot arguments
        kwargs = {}
        if self.args.type == 'StackedLine':
            kwargs.update({'fill': True})

        # create chart
        chart = getattr(pygal, self.args.type)(**kwargs)     # set chart type

        ############################################################
        #                           Create plots                   #
        ############################################################
        if self.args.type in ['Line', 'StackedLine', 'Bar', 'StackedBar']:
            for col in series:
                if col.type not in [float, int]:     # skip non-numeric columns
                    continue
                chart.add(col.name, col)

            if x:
                chart.x_labels = map(str, x)

        elif self.args.type in ['XY']:
            if not x or len(series) == 1:
                raise Exception("Please specify X and Y series")
            y = series[0]
            chart.add(y.name, zip(x, y))
        else:
            raise Exception("Chart type is not supported")

        chart.title = self.args.title

        # output chart
        if self.args.output == 'browser':  # default: browser
            chart.render_in_browser()
        else:
            extension = os.path.splitext(self.args.output)[1]
            print self.args.output, extension
            if extension == '.png':
                chart.render_to_png(self.args.output)
            elif extension == '.svg':
                chart.render_to_file(self.args.output)
            else:
                raise Exception(
                    "Unsupported file extension: Possible values are 'png' and 'svg'")


def launch_new_instance():
    utility = CSVPlot()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
