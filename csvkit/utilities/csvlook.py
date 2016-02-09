#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility


class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')

    def main(self):
        table = agate.Table.from_csv(self.input_file, sniff_limit=self.args.sniff_limit, header=not self.args.no_header_row, column_types=self.get_column_types(), line_numbers=self.args.line_numbers, **self.reader_kwargs)
        table.print_table(output=self.output_file)


def launch_new_instance():
    utility = CSVLook()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
