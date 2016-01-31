#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility


class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'

    def add_arguments(self):
        pass

    def main(self):
        agate.Table.from_csv(self.input_file, header=not self.args.no_header_row, **self.reader_kwargs).print_table(output=self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVLook()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
