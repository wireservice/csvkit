#!/usr/bin/env python

import os
import sys

from csvkit import sql
from csvkit import table
from csvkit.cli import CSVKitUtility

class CSVSQL(CSVKitUtility):
    description = 'Generate a SQL CREATE TABLE statement for a CSV file.'
    override_flags = 'l'

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes.')
        self.argparser.add_argument('-i', '--dialect', dest='dialect', choices=sql.DIALECTS,
                            help='Dialect of SQL to generate.')
        self.argparser.add_argument('--inserts', dest='inserts', action='store_true',
                            help='In addition to generating a CREATE TABLE statement, also generate an INSERT statement for each row of data.')

    def main(self):
        if self.args.file.name != '<stdin>':
            # Use filename as table name
            table_name = os.path.splitext(os.path.split(self.args.file.name)[1])[0]
        else:
            table_name = 'csvsql_table'

        csv_table = table.Table.from_csv(self.args.file, name=table_name, snifflimit=self.args.snifflimit, **self.reader_kwargs)
        sql_table = sql.make_table(csv_table)

        self.output_file.write((u'%s\n' % sql.make_create_table_statement(sql_table, dialect=self.args.dialect)).encode('utf-8'))

        if self.args.inserts:
            self.output_file.write('\n')
            for row in csv_table.to_rows(serialize_dates=True):
                self.output_file.write((u'%s\n' % sql.make_insert_statement(sql_table, row, dialect=self.args.dialect)).encode('utf-8'))

if __name__ == '__main__':
    utility = CSVSQL()
    utility.main()
