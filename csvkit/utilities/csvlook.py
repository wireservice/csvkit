#!/usr/bin/env python

import itertools

import agate
import six

from csvkit.cli import CSVKitUtility
from csvkit.headers import make_default_headers


class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'

    def add_arguments(self):
        pass

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

        agate.Table(list(rows)).print_table(output=self.output_file)


def launch_new_instance():
    utility = CSVLook()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
