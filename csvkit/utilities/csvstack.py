#!/usr/bin/env python

import os.path
import sys

import agate

from csvkit.cli import CSVKitUtility, isatty, make_default_headers


def _skip_lines(f, args):
    if isinstance(args.skip_lines, int):
        skip_lines = args.skip_lines
        while skip_lines > 0:
            f.readline()
            skip_lines -= 1
    else:
        raise ValueError('skip_lines argument must be an int')

    return skip_lines


class CSVStack(CSVKitUtility):
    description = 'Stack up the rows from multiple CSV files, optionally adding a grouping value.'
    # Override 'f' because the utility accepts multiple files.
    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument(
            metavar='FILE', nargs='*', dest='input_paths', default=['-'],
            help='The CSV file(s) to operate on. If omitted, will accept input as piped data via STDIN.')
        self.argparser.add_argument(
            '-g', '--groups', dest='groups',
            help='A comma-separated list of values to add as "grouping factors", one per CSV being stacked. These are '
                 'added to the output as a new column. You may specify a name for the new column using the -n flag.')
        self.argparser.add_argument(
            '-n', '--group-name', dest='group_name',
            help='A name for the grouping column, e.g. "year". Only used when also specifying -g.')
        self.argparser.add_argument(
            '--filenames', dest='group_by_filenames', action='store_true',
            help='Use the filename of each input file as its grouping value. When specified, -g will be ignored.')

    def main(self):
        if isatty(sys.stdin) and self.args.input_paths == ['-']:
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        has_groups = self.args.groups is not None or self.args.group_by_filenames

        if self.args.groups is not None and not self.args.group_by_filenames:
            groups = self.args.groups.split(',')

            if len(groups) != len(self.args.input_paths):
                self.argparser.error(
                    'The number of grouping values must be equal to the number of CSV files being stacked.')
        else:
            groups = None

        group_name = self.args.group_name if self.args.group_name else 'group'
        use_fieldnames = not self.args.no_header_row

        if use_fieldnames:
            Reader = agate.csv.DictReader
        else:
            Reader = agate.csv.reader

        headers = []
        stdin_fieldnames = []
        stdin_first_row = []

        for path in self.args.input_paths:
            f = self._open_input_file(path)
            file_is_stdin = path == '-'

            _skip_lines(f, self.args)
            rows = Reader(f, **self.reader_kwargs)

            if use_fieldnames:
                for field in rows.fieldnames:
                    if field not in headers:
                        headers.append(field)

                # If the file is standard input, store the fieldnames so that the rows can be read correctly later.
                if file_is_stdin:
                    stdin_fieldnames = rows.fieldnames
                else:
                    f.close()
            else:
                row = next(rows, [])
                headers = list(make_default_headers(len(row)))

                # If the file is standard input, store the row that was used to calculate the number of columns.
                if file_is_stdin:
                    stdin_first_row = row
                else:
                    f.close()

                # If we aren't using header rows, we only look at the first file and stack columns in the same order.
                break

        if has_groups:
            headers.insert(0, group_name)

        if use_fieldnames:
            output = agate.csv.DictWriter(self.output_file, fieldnames=headers, **self.writer_kwargs)
            output.writeheader()
        else:
            output = agate.csv.writer(self.output_file, **self.writer_kwargs)
            output.writerow(headers)

        for i, path in enumerate(self.args.input_paths):
            f = self._open_input_file(path, opened=True)
            file_is_stdin = path == '-'

            if has_groups:
                if groups:
                    group = groups[i]
                else:
                    group = os.path.basename(f.name)

            # If the file is standard input, we've already skipped any lines above, to find its header row.
            if not file_is_stdin:
                _skip_lines(f, self.args)

            # If the file is standard input, we've already read the header row, so we need to provide it here.
            kwargs = {}
            if file_is_stdin and use_fieldnames:
                kwargs['fieldnames'] = stdin_fieldnames

            rows = Reader(f, **self.reader_kwargs, **kwargs)

            # If the file is standard input, we need to add back the row we used to calculate the number of columns.
            if file_is_stdin and stdin_first_row:
                output.writerow(stdin_first_row)

            for row in rows:
                if has_groups:
                    if use_fieldnames:
                        row[group_name] = group
                    else:
                        row.insert(0, group)

                output.writerow(row)

            f.close()


def launch_new_instance():
    utility = CSVStack()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
