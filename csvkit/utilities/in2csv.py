#!/usr/bin/env python

import agate
import agatedbf  # noqa
import agateexcel  # noqa

from csvkit import convert
from csvkit.convert.fixed import fixed2csv
from csvkit.convert.geojs import geojson2csv
from csvkit.cli import CSVKitUtility

SUPPORTED_FORMATS = ['csv', 'dbf', 'fixed', 'geojson', 'json', 'ndjson', 'xls', 'xlsx']


class In2CSV(CSVKitUtility):
    description = 'Convert common, but less awesome, tabular data formats to CSV.'
    epilog = 'Some command-line flags only pertain to specific input formats.'
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument(metavar="FILE", nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-f', '--format', dest='filetype',
                                    help='The format of the input file. If not specified will be inferred from the file type. Supported formats: %s.' % ', '.join(sorted(SUPPORTED_FORMATS)))
        self.argparser.add_argument('-s', '--schema', dest='schema',
                                    help='Specifies a CSV-formatted schema file for converting fixed-width files.  See documentation for details.')
        self.argparser.add_argument('-k', '--key', dest='key',
                                    help='Specifies a top-level key to use look within for a list of objects to be converted when processing JSON.')
        self.argparser.add_argument('--sheet', dest='sheet',
                                    help='The name of the XLSX sheet to operate on.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing CSV input.')

    def main(self):
        # Determine the file type.
        if self.args.filetype:
            filetype = self.args.filetype
            if filetype not in SUPPORTED_FORMATS:
                self.argparser.error('"%s" is not a supported format' % self.args.filetype)
        elif self.args.schema:
            filetype = 'fixed'
        elif self.args.key:
            filetype = 'json'
        else:
            if not self.args.input_path or self.args.input_path == '-':
                self.argparser.error('You must specify a format when providing data via STDIN (pipe).')
            filetype = convert.guess_format(self.args.input_path)
            if not filetype:
                self.argparser.error('Unable to automatically determine the format of the input file. Try specifying a format with --format.')

        self.buffers_input = filetype == 'csv' or not self.args.no_inference

        # Set the input file.
        if filetype in ('xls', 'xlsx'):
            self.input_file = open(self.args.input_path, 'rb')
        else:
            self.input_file = self._open_input_file(self.args.input_path)

        # Set the reader's arguments.
        kwargs = {}

        if self.args.schema:
            schema = self._open_input_file(self.args.schema)
        elif filetype == 'fixed':
            raise ValueError('schema must not be null when format is "fixed"')

        if self.args.sheet:
            kwargs['sheet'] = self.args.sheet

        if filetype == 'csv':
            kwargs.update(self.reader_kwargs)
            # Streaming CSV musn't set sniff_limit, but non-streaming should.
            if not self.args.no_inference:
                kwargs['sniff_limit'] = self.args.sniff_limit
            if self.args.no_header_row:
                kwargs['header'] = False
        elif self.args.no_inference:
            # Streaming CSV musn't set column_types, but other formats should.
            kwargs['column_types'] = agate.TypeTester(limit=0)

        # Convert the file.
        if filetype == 'csv' and self.args.no_inference:
            reader = agate.csv.reader(self.input_file, **self.reader_kwargs)
            writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
            writer.writerows(reader)
        elif filetype == 'fixed':
            self.output_file.write(fixed2csv(self.input_file, schema, output=self.output_file, **kwargs))
        elif filetype == 'geojson':
            self.output_file.write(geojson2csv(self.input_file, **kwargs))
        elif filetype in ('csv', 'dbf', 'json', 'ndjson', 'xls', 'xlsx'):
            if filetype == 'csv':
                table = agate.Table.from_csv(self.input_file, **kwargs)
            elif filetype == 'json':
                table = agate.Table.from_json(self.input_file, key=self.args.key, **kwargs)
            elif filetype == 'ndjson':
                table = agate.Table.from_json(self.input_file, key=self.args.key, newline=True, **kwargs)
            elif filetype == 'xls':
                table = agate.Table.from_xls(self.input_file, sheet=kwargs.get('sheet'))
            elif filetype == 'xlsx':
                table = agate.Table.from_xlsx(self.input_file, sheet=kwargs.get('sheet'))
            elif filetype == 'dbf':
                if not hasattr(self.input_file, 'name'):
                    raise ValueError('DBF files can not be converted from stdin. You must pass a filename.')
                table = agate.Table.from_dbf(self.input_file.name, **kwargs)
            table.to_csv(self.output_file)

        self.input_file.close()

        if self.args.schema:
            schema.close()


def launch_new_instance():
    utility = In2CSV()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
