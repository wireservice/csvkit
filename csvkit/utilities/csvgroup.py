#!/usr/bin/env python

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, match_column_identifier
from csvkit.group import group_rows


class CSVGroup(CSVKitUtility):
    description = 'Execute a SQL-like group by on specified column or colums'

    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='The column name(s) on which to group by. Should be either one name (or index) or a comma-separated list. May also be left unspecified, in which case all columns will be used')
        self.argparser.add_argument('-n', '--count', dest='count_column_name', nargs='?', const='count',
            default=None,
            help='Generate a new column containing the count of rows in this group. Specify a name for the new column, or the name "count" will be used"')

        self.argparser.add_argument('-g', '--grouped_only', dest='grouped_only',
            action='store_true',
            help='Only include the grouped columns in the output'
        )

    def main(self, group=True, write=True):
        if self.args.columns:
            grouped_columns = self._parse_column_names(self.args.columns)
        else:
            grouped_columns = []

        #Read in header and rows
        reader = CSVKitReader(self.args.file, **self.reader_kwargs)
        header = reader.next()
        rows = list(reader)

        #Determine columns to group by, default to all columns
        if not grouped_columns:
            grouped_columns = [x for x in range(1,len(header) + 1)]
        grouped_column_ids = [match_column_identifier(header, c) \
                              for c in grouped_columns]

        #Perform the grouping
        if group:
            table = group_rows(header, rows, grouped_column_ids, self.args.count_column_name,
                              self.args.grouped_only)

        #Write the output
        if write:
            output = CSVKitWriter(self.output_file, **self.writer_kwargs)
            for row in table:
                output.writerow(row)

def launch_new_instance():
    utility = CSVGroup()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
