#!/usr/bin/env python

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility 

class CSVFormat(CSVKitUtility):
    description = 'Convert a CSV file to a custom output format.'
    override_flags = ['l', 'zero', 'H']

    def add_arguments(self):
        self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
            help='Delimiting character of the output CSV file.')
        self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
            help='Specifies that the output CSV file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
            help='Character used to quote strings in the output CSV file.')
        self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0,1,2,3],
            help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument('-B', '--out-doublequote', dest='out_doublequote', action='store_true',
            help='Whether or not double quotes are doubled in the output CSV file.')
        self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
            help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --doublequote is not specified.')
        self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
            help='Character used to terminate lines in the output CSV file.')

    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        if self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter

        if self.args.out_quotechar:
            kwargs['quotechar'] = self.args.out_quotechar

        if self.args.out_quoting:
            kwargs['quoting'] = self.args.out_quoting

        if self.args.out_doublequote:
            kwargs['doublequote'] = self.args.out_doublequote

        if self.args.out_escapechar:
            kwargs['escapechar'] = self.args.out_escapechar

        if self.args.out_lineterminator:
            kwargs['lineterminator'] = self.args.out_lineterminator

        return kwargs

    def main(self):
        reader = CSVKitReader(self.input_file, **self.reader_kwargs)

        writer = CSVKitWriter(self.output_file, **self.writer_kwargs)

        writer.writerows(reader)

def launch_new_instance():
    utility = CSVFormat()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

