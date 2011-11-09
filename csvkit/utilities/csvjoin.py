#!/usr/bin/env python

from csvkit import CSVKitReader, CSVKitWriter
from csvkit import join
from csvkit.cli import CSVFileType, CSVKitUtility, match_column_identifier

class CSVJoin(CSVKitUtility):
    description = 'Execute a SQL-like join to merge CSV files on a specified column or columns.'
    epilog = 'Note that the join operation requires reading all files into memory. Don\'t try this on very large files.'
    override_flags = 'f'
    
    def add_arguments(self):
        self.argparser.add_argument('files', metavar="FILES", nargs='+', type=CSVFileType(),
            help='The CSV files to operate on. If only one is specified, it will be copied to STDOUT.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='The column name(s) on which to join. Should be either one name (or index) or a comma-separated list with one name (or index) for each file, in the same order that the files were specified. May also be left unspecified, in which case the two files will be joined sequentially without performing any matching.')
        self.argparser.add_argument('--outer', dest='outer_join', action='store_true',
            help='Perform a full outer join, rather than the default inner join.')
        self.argparser.add_argument('--left', dest='left_join', action='store_true',
            help='Perform a left outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of left outer joins, starting at the left.')
        self.argparser.add_argument('--right', dest='right_join', action='store_true',
            help='Perform a right outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of right outer joins, starting at the right.')

    def main(self):
        if len(self.args.files) < 2:
            self.argparser.error('You must specify at least two files to join.')

        if self.args.columns:
            join_column_names = self._parse_join_column_names(self.args.columns)

            if len(join_column_names) == 1:
                join_column_names = join_column_names * len(self.args.files)

            if len(join_column_names) != len(self.args.files):
                self.argparser.error('The number of join column names must match the number of files, or be a single column name that exists in all files.')

        if (self.args.left_join or self.args.right_join or self.args.outer_join) and not self.args.columns:
            self.argparser.error('You must provide join column names when performing an outer join.')

        if self.args.left_join and self.args.right_join:
             self.argparser.error('It is not valid to specify both a left and a right join.')

        tables = []

        for f in self.args.files:
            tables.append(list(CSVKitReader(f, **self.reader_kwargs)))

        join_column_ids = []
        
        if self.args.columns:
            for i, t in enumerate(tables):
                join_column_ids.append(match_column_identifier(t[0], join_column_names[i]))

        jointab = []
        
        if self.args.left_join:
            # Left outer join
            jointab = tables[0]

            for i, t in enumerate(tables[1:]):
                jointab = join.left_outer_join(jointab, join_column_ids[0], t, join_column_ids[i + 1])
        elif self.args.right_join:
            # Right outer join
            jointab = tables[-1]

            remaining_tables = tables[:-1]
            remaining_tables.reverse()

            for i, t in enumerate(remaining_tables):
                jointab = join.right_outer_join(t, join_column_ids[-(i + 2)], jointab, join_column_ids[-1])
        elif self.args.outer_join:
            # Full outer join
            jointab = tables[0]

            for i, t in enumerate(tables[1:]):
                jointab = join.full_outer_join(jointab, join_column_ids[0], t, join_column_ids[i + 1])
        else:
            if self.args.columns:
                # Inner join
                jointab = tables[0]

                for i, t in enumerate(tables[1:]):
                    jointab = join.inner_join(jointab, join_column_ids[0], t, join_column_ids[i + 1])
            else:
                jointab = tables[0]

                # Sequential join
                for t in tables[1:]:
                    jointab = join.sequential_join(jointab, t)

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)

        for row in jointab:
            output.writerow(row)

    def _parse_join_column_names(self, join_string):
        """
        Parse a list of join columns.
        """
        return map(str.strip, join_string.split(','))
    
if __name__ == '__main__':
    utility = CSVJoin()
    utility.main()
