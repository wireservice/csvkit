#!/usr/bin/env python

import itertools

import agate
import six

from csvkit.cli import CSVKitUtility
from csvkit.headers import make_default_headers

class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'

    def add_arguments(self):
        self.argparser.add_argument(
            '-L', '--linestyle', dest='linestyle', default="ascii",
            help='output table line style, one of ascii or unicode')

    def main(self):
        rows = agate.reader(self.input_file, **self.reader_kwargs)

        # Make a default header row if none exists
        if self.args.no_header_row:
            row = next(rows)

            column_names = make_default_headers(len(row))

            # Put the row back on top
            rows = itertools.chain([row], rows)
        else:
            column_names = next(rows)

        column_names = list(column_names)

        # prepend 'line_number' column with line numbers if --linenumbers option
        if self.args.line_numbers:
            column_names.insert(0, 'line_number')
            rows = [list(itertools.chain([str(i + 1)], row)) for i, row in enumerate(rows)]


        # Convert to normal list of rows
        rows = list(rows)

        # Insert the column names at the top
        rows.insert(0, column_names)

        widths = []

        for row in rows:
            for i, v in enumerate(row):
                try:
                    if len(v) > widths[i]:
                        widths[i] = len(v)
                except IndexError:
                    widths.append(len(v))

        if self.args.linestyle == 'unicode':
            l_h = b"\342\224\200".decode('utf-8')
            l_v = b"\342\224\202".decode('utf-8')
            # [t]op [b]ottom [l]eft [r]ight
            # direction indicates which edges have 'spokes'
            # corners
            l_br = b"\342\224\214".decode('utf-8')
            l_tr = b"\342\224\224".decode('utf-8')
            l_bl = b"\342\224\220".decode('utf-8')
            l_tl = b"\342\224\230".decode('utf-8')
            # cross, internal intersection
            l_tblr = b"\342\224\274".decode('utf-8')
            # outer edge intersections
            l_tbl = b"\342\224\244".decode('utf-8')
            l_tbr = b"\342\224\234".decode('utf-8')
            l_tlr = b"\342\224\264".decode('utf-8')
            l_blr = b"\342\224\254".decode('utf-8')
            top_divider = \
                l_br+l_h+l_h + \
                (l_h+l_blr+l_h).join(l_h * w for w in widths) + \
                l_h+l_h+l_bl
            mid_divider =\
                l_tbr+l_h+l_h + \
                (l_h+l_tblr+l_h).join(l_h * w for w in widths) + \
                l_h+l_h+l_tbl
            bot_divider = \
                l_tr+l_h+l_h + \
                (l_h+l_tlr+l_h).join(l_h * w for w in widths) + \
                l_h+l_h+l_tl
        else:
            # Dashes span each width with '+' character at
            # intersection of horizontal and vertical dividers.
            top_divider = mid_divider = bot_divider = \
                '|--' + '-+-'.join('-'* w for w in widths) + '--|'
            l_v = '|'

        self.output_file.write('%s\n' % top_divider)

        for i, row in enumerate(rows):
            output = []

            for j, d in enumerate(row):
                if d is None:
                    d = ''
                output.append(' %s ' % six.text_type(d).ljust(widths[j]))

            self.output_file.write((l_v + ' %s ' + l_v + '\n') % (l_v.join(output)))

            if (i == 0):
                self.output_file.write('%s\n' % mid_divider)
            elif i == (len(rows) - 1):
                self.output_file.write('%s\n' % bot_divider)

def launch_new_instance():
    utility = CSVLook()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
