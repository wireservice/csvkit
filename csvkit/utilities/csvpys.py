#!/usr/bin/env python

import sys

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, CSVFileType
from csvkit.script import ScriptCSVReader


class CSVScript(CSVKitUtility):
    description = 'Python scripting in CSV files, allowing to save processing result as new csv columns.'
    override_flags = 'f'


    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-s', '--script', dest='script', action='append',
                                    help='New column name and a python script. -c "<NEW_COLUMN_NAME>|<PYTHON SCRIPT>". Inside script use c[0] or ch[\'header\'] locals.')

        self.argparser.add_argument('file', metavar="FILE", nargs='?', type=CSVFileType(), default=sys.stdin,
                                    help='The CSV file to operate on. If omitted, will accept input on STDIN.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if not self.args.script:
            self.argparser.error("At least one script -s must be defined.")

        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        script_reader = ScriptCSVReader(rows, scripts=self.args.script, zero_based=self.args.zero_based)
        for i, row in enumerate(script_reader):
            output.writerow(row)


def launch_new_instance():
    utility = CSVScript()
    utility.main()


if __name__ == "__main__":
    launch_new_instance()

