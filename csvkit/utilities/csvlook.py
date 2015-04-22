#!/usr/bin/env python

import itertools

import six

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility
from csvkit.headers import make_default_headers

class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'

    def add_arguments(self):
        self.argparser.add_argument('-w', '--wrap', dest='wrapwidth', type=int,
            help='Columns wrapwidth (allows to view long fields in multilines).', default=60)

    def main(self):
        rows = CSVKitReader(self.input_file, **self.reader_kwargs)
        max_chars = self.args.wrapwidth

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

        # Work out column widths
        widths = []
        for row in rows:
            for i, v in enumerate(row):
                lv = min(len(v), max_chars)
                try:
                    if lv > widths[i]:
                        widths[i] = lv
                except IndexError:
                    widths.append(lv)

        # Dashes span each width with '+' character at intersection of
        # horizontal and vertical dividers.
        divider = '|--' + '-+-'.join('-'* w for w in widths) + '--|'

        self.output_file.write('%s\n' % divider)

        for i, row in enumerate(rows):
            # Each row is made of inner rows because of text wrapping
            row = [d or '' for d in row]
            n_inner_rows = int(max([len(d)-1 for d in row]) / max_chars) + 1
            inner_rows = [[d[j*max_chars:(j+1)*max_chars] for d in row]
                    for j in range(n_inner_rows)]

            for inner_row in inner_rows:
                output = []
                for j, d in enumerate(inner_row):
                    output.append(' %s ' % six.text_type(d).ljust(widths[j]))

                self.output_file.write('| %s |\n' % ('|'.join(output)))

            if (i == 0 or i == len(rows) - 1):
                self.output_file.write('%s\n' % divider)

def launch_new_instance():
    utility = CSVLook()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()

