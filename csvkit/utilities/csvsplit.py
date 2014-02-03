#!/usr/bin/env python

import collections
import itertools

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.headers import make_default_headers

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

class FileWritersPool(object):
    def __init__(self, file_constructor, writer_kwargs):
        self.file_constructor = file_constructor
        self.writer_kwargs = writer_kwargs
        self.writers = {}
        # TODO: replace with a number dependent on the max opened files on this system
        self.last_used = collections.deque(maxlen=100)
        self.opened_fobjs = {}

    def get_writer(self, name):
        self.last_used.append(name)
        return self.writers[name]

    def create_writer(self, name, fname):
        try:
            if name in self.opened_fobjs:
                mode = "a"
            else:
                mode = "w"
            fobj = self.file_constructor(fname, mode, **self.writer_kwargs)
            self.writers[name] = CSVKitWriter(fobj)
            self.opened_fobjs[name] = fobj
        except IOError:
            # Too many open files, close the recently not used
            for k in self.writers:
                if k not in self.last_used and k in self.opened_fobjs:
                    self.opened_fobjs.pop(k).close()
            fobj = self.file_constructor(fname, mode, **self.writer_kwargs)
            self.writers[name] = CSVKitWriter(fobj)
            self.opened_fobjs[name] = fobj



class CSVSplit(CSVKitUtility):
    description = 'Split CSV files according to values in specified columns. Opposite to what CSV Stack does.'
    #override_flags = ['f', 'H']

    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                        help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-o', '--output', dest='output',
                        help='The output filename template. The value of the specified columns will be added right before the extension. It must be specified if reading from STDIN.')


    def main(self, file_constructor=open):
        # file_constructor parameter is used to test without creating files
        if not self.args.columns:
            self.argparser.error('You must specify at least one column to search using the -c option.')

        rows = CSVKitReader(self.args.file, **self.reader_kwargs)

        if self.args.no_header_row:
            row = rows.next()

            column_names = make_default_headers(len(row))

            # Put the row back on top
            rows = itertools.chain([row], rows)
        else:
            column_names = rows.next()


        column_ids = parse_column_identifiers(self.args.columns, column_names, self.args.zero_based)
        
        try:
            basename = self.args.file._lazy_args[0]
        except AttributeError:
            basename = self.args.output
            if not basename:
                self.argparser.error('You must specify the output filename template when you are reading from STDIN.')

        writers_pool = FileWritersPool(file_constructor, self.writer_kwargs)
        for row in rows:
            grouping_values = tuple([row[c] if c < len(row) else None for c in column_ids])
            try:
                writers_pool.get_writer(grouping_values)\
                    .writerow(row)
            except KeyError:
                fname = fname_format(basename, '_'.join(grouping_values))
                writers_pool.create_writer(grouping_values, fname)
                writer = writers_pool.get_writer(grouping_values)
                if not self.args.no_header_row:
                    writer.writerow(column_names)
                writer.writerow(row)


def launch_new_instance():
    utility = CSVSplit()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

