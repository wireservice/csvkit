#!/usr/bin/env python

"""
csvtranspose
"""

import agate

from csvkit.cli import CSVKitUtility


class CSVTranspose(CSVKitUtility):
    description = 'Transpose CSV data.'

    def add_arguments(self):
        pass

    def main(self):
        self.args.columns = None
        self.args.no_header_row = True

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**self.reader_kwargs)
        rows = list(map(list, zip(*rows)))

        column_names = list(rows[0])
        column_ids = range(len(column_names))
        rows = rows[1:]

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)
        output.writerow([column_names[column_id] for column_id in column_ids])

        for row in rows:
            out_row = [row[column_id] if column_id < len(row) else None for column_id in column_ids]
            output.writerow(out_row)


def launch_new_instance():
    utility = CSVTranspose()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
