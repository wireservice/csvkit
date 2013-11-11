#!/usr/bin/env python
from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers


class CSV2TSV(CSVKitUtility):
    description = 'Convert CSV to TSV or other delimited format.'

    def add_arguments(self):
        self.argparser.add_argument('-D', '--outputdelimiter',
            dest='output_delimiter', default='\t',
            help='Delimiting character of output defaults to tab.')
        self.argparser.add_argument('-Q', '--outputquotechar',
            dest='output_quotechar', default='"',
            help='Output quote character. Defaults to ".')
        self.argparser.add_argument('-U', '--outputquoting',
            dest='output_quoting', type=int, choices=[0,1,2,3], default=0,
            help='Quoting style used for output. ' \
                '0 = Quote Minimal (default), 1 = Quote All, ' \
                '2 = Quote non-numeric, 3 = Quote None')

    def main(self):
        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = rows.next()
        column_ids = parse_column_identifiers([], column_names,
            self.args.zero_based)
        output = CSVKitWriter(self.output_file,
            delimiter=self.args.output_delimiter,
            quoting=self.args.output_quoting,
            quotechar=self.args.output_quotechar, **self.writer_kwargs)
        output.writerow([column_names[c] for c in column_ids])
        for i, row in enumerate(rows):
            output.writerow(row)


def launch_new_instance():
    utility = CSV2TSV()
    utility.main() 


if __name__ == "__main__":
    launch_new_instance()
