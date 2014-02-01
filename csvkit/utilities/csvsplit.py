#!/usr/bin/env python

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers

def fname_format(fname, label):
    """Return a filename with a label, inserted right before the last file extension.

    For example "data/population.projection.csv" with label `2009` becomes
    "data/population.projection_2009.csv".

    """
    parts = fname.split(".")
    if len(parts) > 1: # We have an extension
        first = '.'.join(parts[:-1])
        ext = ".{}".format(parts[-1])
    else: # No extension
        first = parts[0]
        ext = ""
    full_fname = "{}_{}{}".format(first, label, ext)
    return full_fname

class CSVSplit(CSVKitUtility):
    description = 'Split CSV files according to values in specified columns. Opposite to what CSV Stack does.'
    #override_flags = ['f', 'H']

    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')

    def main(self, file_constructor=open):
        # file_constructor parameter is used to test without creating files
        if not self.args.columns:
            self.argparser.error('You must specify at least one column to search using the -c option.')

        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = rows.next()

        column_ids = parse_column_identifiers(self.args.columns, column_names, self.args.zero_based)
        
        # FIXME: assign output basename/fname in case of reading from STDIN
        self.writers = {}
        for row in rows:
            grouping_values = tuple([row[c] if c < len(row) else None for c in column_ids])
            try:
                self.writers[grouping_values].writerow(row)
            except KeyError:
                fname = "./"+fname_format(self.args.file._lazy_args[0], '_'.join(grouping_values))
                writer = CSVKitWriter(file_constructor(fname, "w", **self.writer_kwargs))
                writer.writerow(column_names)
                writer.writerow(row)
                self.writers[grouping_values] = writer


def launch_new_instance():
    utility = CSVSplit()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

