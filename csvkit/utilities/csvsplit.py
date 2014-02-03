#!/usr/bin/env python

import collections
import itertools
import os.path

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.headers import make_default_headers

def fname_format(fname, label):
    """
    Return a filename with a label, inserted right before the last file extension.

    For example "data/population.projection.csv" with label `2009` becomes
    "data/population.projection_2009.csv".

    """
    root, ext = os.path.splitext(fname)
    full_fname = "{}_{}{}".format(root, label, ext)
    return full_fname

class FileWritersPool(object):
    """
    Manages a pool of open files and CSV Writers, so that we don't have to open and
    close them continuously. When the number of files is more that the system can
    handle, closes those that were not used recently.

    """
    def __init__(self, file_constructor, writer_kwargs):
        self.file_constructor = file_constructor
        self.writer_kwargs = writer_kwargs
        self.writers = {}
        # TODO: replace with a number dependent on the max opened files on this system
        self.last_used = collections.deque(maxlen=100)
        self.opened_fobjs = {}

    def get_writer(self, fname):
        self.last_used.append(fname)
        try:
            return self.writers[fname]
        except KeyError:
            return self._create_writer(fname)

    def _create_writer(self, fname):
        if fname in self.opened_fobjs:
            mode = "a"
        else:
            mode = "w"
        try:
            fobj = self.file_constructor(fname, mode, **self.writer_kwargs)  
        except IOError:
            # Too many open files, close those not recently used and try again
            to_be_closed = [fw for fw in self.writers
                if fw not in self.last_used
                and fw not in self.opened_fobjs]
            for fw in to_be_closed:
                self.opened_fobjs[fw].close()
                self.writers.pop(fw)

        self.opened_fobjs[fname] = fobj
        self.writers[fname] = CSVKitWriter(fobj)
        return self.writers[fname]



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
            fname = fname_format(basename, '_'.join(grouping_values))
            writers_pool.get_writer(fname).writerow(row)
            if not self.args.no_header_row:
                writer.writerow(column_names)


def launch_new_instance():
    utility = CSVSplit()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

