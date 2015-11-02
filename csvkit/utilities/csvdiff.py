#!/usr/bin/env python

import sys
import daff

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, match_column_identifier

class CSVDiff(CSVKitUtility):
    description = 'Compare CSV files. Like unix "diff" command, but for tabular data.'
    epilog = 'Note that the diff operation requires reading all files into memory. Don\'t try this on very large files.'
    override_flags = ['f', 'H']

    def add_arguments(self):
        self.argparser.add_argument(metavar="FILE", nargs='*', dest='input_paths', default=['-'],
            help='The CSV files to operate on.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='The column name(s) to use for comparison. Should be either one name or a comma-separated list of names. May also be left unspecified, in which case we\'ll guess something plausible.')
        self.argparser.add_argument('--color', dest='color', action='store_true',
            help='Decorate output with colors and glyphs.')

    def main(self):
        self.input_files = []

        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        ct = len(self.input_files)
        if ct < 2:
            self.argparser.error('You must specify two or three files to compare.\n(If three, the first file should be a common ancestor of the remaining two)')
        if ct > 3:
            self.argparser.error('You must specify at most three files to compare.')

        match_column_names = []
        if self.args.columns:
            match_column_names = self._parse_match_column_names(self.args.columns)

        tables = []

        for f in self.input_files:
            tables.append(list(CSVKitReader(f, **self.reader_kwargs)))
            f.close()

        flags = daff.CompareFlags()
        for c in match_column_names:
            flags.addPrimaryKey(c)

        result = []
        tab = daff.PythonTableView(result)
        tab1 = daff.PythonTableView(tables[ct-2])
        tab2 = daff.PythonTableView(tables[ct-1])
        if ct == 3:
            tab0 = daff.PythonTableView(tables[0])
            alignment = daff.Coopy.compareTables3(tab0,tab1,tab2,flags).align()
        else:
            alignment = daff.Coopy.compareTables(tab1,tab2,flags).align()
        daff.TableDiff(alignment,flags).hilite(tab)

        if self.args.color or (self.output_file == sys.stdout and sys.stdout.isatty()):
            self.output_file.write(daff.TerminalDiffRender().render(tab).encode('utf-8'))
        else:
            output = CSVKitWriter(self.output_file, **self.writer_kwargs)
            for row in result:
                output.writerow(row)

    def _parse_match_column_names(self, join_string):
        """
        Parse a list of match columns.
        """
        return list(map(str.strip, join_string.split(',')))


def launch_new_instance():
    utility = CSVDiff()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
