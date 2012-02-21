#!/usr/bin/env python

import os
import sys

from csvkit import sql
from csvkit import table
from csvkit.cli import CSVKitUtility

class CSVSQL(CSVKitUtility):
    description = 'Generate SQL statements for a CSV file or create execute those statements directly on a database.'
    override_flags = 'l'

    def add_arguments(self):
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes.')
        self.argparser.add_argument('-i', '--dialect', dest='dialect', choices=sql.DIALECTS,
                            help='Dialect of SQL to generate. Only valid when --db is not specified.')
        self.argparser.add_argument('--db', dest='connection_string',
                            help='If present, a sqlalchemy connection string to use to directly execute generated SQL on a database.')
        self.argparser.add_argument('--insert', dest='insert', action='store_true',
                            help='In addition to creating the table, also insert the data into the table. Only valid when --db is specified.')
        self.argparser.add_argument('--table', dest='table_name',
                            help='Specify a name for the table to be created. If omitted, the filename (minus extension) will be used.')
        self.argparser.add_argument('--no-constraints', dest='no_constraints', action='store_true',
                            help='Generate a schema without length limits or null checks. Useful when sampling big tables.')

    def main(self):
        if self.args.table_name:
            table_name = self.args.table_name
        elif self.args.file != sys.stdin:
            # Use filename as table name
            table_name = os.path.splitext(os.path.split(self.args.file.name)[1])[0]
        else:
            self.argparser.error('The --table argument is required when providing data over STDIN.')

        if self.args.dialect and self.args.connection_string:
            self.argparser.error('The --dialect option is only valid when --db is not specified.')

        if self.args.insert and not self.args.connection_string:
            self.argparser.error('The --insert option is only valid when --db is also specified.')

        csv_table = table.Table.from_csv(self.args.file, name=table_name, snifflimit=self.args.snifflimit, **self.reader_kwargs)

        # Direct connections to database
        if self.args.connection_string:
            try:
                engine, metadata = sql.get_connection(self.args.connection_string)
            except ImportError:
                raise ImportError('You don\'t appear to have the necessary database backend installed for connection string you\'re trying to use.. Available backends include:\n\nPostgresql:\tpip install psycopg2\nMySQL:\t\tpip install MySQL-python\n\nFor details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at: \n\nhttp://www.sqlalchemy.org/docs/dialects/\n\n')

            sql_table = sql.make_table(csv_table, table_name, self.args.no_constraints, metadata)
            sql_table.create()

            if self.args.insert:
                insert = sql_table.insert()
                headers = csv_table.headers()

                conn = engine.connect()
                trans = conn.begin()
                for row in csv_table.to_rows():
                    conn.execute(insert, [dict(zip(headers, row)), ])
                trans.commit()
                conn.close()

        # Writing to file
        else:
            sql_table = sql.make_table(csv_table, table_name, self.args.no_constraints)
            self.output_file.write((u'%s\n' % sql.make_create_table_statement(sql_table, dialect=self.args.dialect)).encode('utf-8'))

if __name__ == '__main__':
    utility = CSVSQL()
    utility.main()

