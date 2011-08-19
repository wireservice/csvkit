#!/usr/bin/env python

import json
import codecs

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility
from csvkit.exceptions import NonUniqueKeyColumnException

class CSVJSON(CSVKitUtility):
    description = 'Convert a CSV file into JSON.'

    def add_arguments(self):
        self.argparser.add_argument('-i', '--indent', dest='indent', type=int, default=None,
            help='Indent the output JSON this many spaces. Disabled by default.')
        self.argparser.add_argument('-k', '--key', dest='key', type=str, default=None,
            help='Output JSON as an array of objects keyed by a given column, KEY, rather than as a list. All values in the column must be unique.')

    def main(self):
        """
        Convert CSV to JSON. 
        """
        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        column_names = rows.next()

        stream = codecs.getwriter('utf-8')(self.output_file)

        if self.args.key:
            output = {}
            
            for row in rows:
                row_dict = dict(zip(column_names, row))
                k = row_dict[self.args.key]

                if k in output:
                    raise NonUniqueKeyColumnException('Value %s is not unique in the key column.' % unicode(k))

                output[k] = row_dict
        else:
            output = [dict(zip(column_names, row)) for row in rows]

        json.dump(output, stream, ensure_ascii=False, indent=self.args.indent, encoding='utf-8')

if __name__ == "__main__":
    CSVJSON().main()

