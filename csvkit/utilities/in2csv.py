#!/usr/bin/env python

from csvkit import convert
from csvkit.cli import CSVKitUtility

class In2CSV(CSVKitUtility):
    description = 'Convert common, but less awesome, tabular data formats to CSV.'
    epilog='Some command line flags only pertain to specific input formats.'
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument(metavar="FILE", nargs='?', dest='input_path',
            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-f', '--format', dest='filetype',
            help='The format of the input file. If not specified will be inferred from the file type. Supported formats: %s.' % ', '.join(sorted(convert.SUPPORTED_FORMATS)))
        self.argparser.add_argument('-s', '--schema', dest='schema',
            help='Specifies a CSV-formatted schema file for converting fixed-width files.  See documentation for details.')
        self.argparser.add_argument('-k', '--key', dest='key',
            help='Specifies a top-level key to use look within for a list of objects to be converted when processing JSON.')
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--sheet', dest='sheet',
            help='The name of the XLSX sheet to operate on.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input.')

    def main(self):
        if self.args.filetype:
            filetype = self.args.filetype

            if filetype not in convert.SUPPORTED_FORMATS:
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

        if filetype in ('xls', 'xlsx'):
            self.input_file = open(self.args.input_path, 'rb')
        else:
            self.input_file = self._open_input_file(self.args.input_path)

        kwargs = self.reader_kwargs

        if self.args.schema:
            kwargs['schema'] = self._open_input_file(self.args.schema)

        if self.args.key:
            kwargs['key'] = self.args.key

        if self.args.snifflimit:
            kwargs['snifflimit'] = self.args.snifflimit

        if self.args.sheet:
            kwargs['sheet'] = self.args.sheet

        if self.args.no_inference:
            kwargs['type_inference'] = False

        if filetype == 'csv' and self.args.no_header_row:
            kwargs['no_header_row'] = True

        # Fixed width can be processed as a stream
        if filetype == 'fixed':
            kwargs['output'] = self.output_file

        data = convert.convert(self.input_file, filetype, **kwargs)

        self.output_file.write(data)

def launch_new_instance():
    utility = In2CSV()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

