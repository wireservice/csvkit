#!/usr/bin/env python

import os
import sys

from csvkit import sql
from csvkit import table
from csvkit import CSVKitWriter
from csvkit.cli import CSVKitUtility

class CSVSQL(CSVKitUtility):
    description = 'Generate SQL statements for one or more CSV files, create execute those statements directly on a database, and execute one or more SQL queries.'
    override_flags = ['l', 'f']

    def add_arguments(self):

        self.argparser.add_argument(metavar="FILE", nargs='*', dest='input_paths', default=['-'],
            help='The CSV file(s) to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-i', '--dialect', dest='dialect', choices=sql.DIALECTS,
            help='Dialect of SQL to generate. Only valid when --db is not specified.')
        self.argparser.add_argument('--db', dest='connection_string',
            help='If present, a sqlalchemy connection string to use to directly execute generated SQL on a database.')
        self.argparser.add_argument('--query', default=None,
            help='Execute one or more SQL queries delimited by ";" and output the result of the last query as CSV.')
        self.argparser.add_argument('--insert', dest='insert', action='store_true',
            help='In addition to creating the table, also insert the data into the table. Only valid when --db is specified.')
        self.argparser.add_argument('--tables', dest='table_names',
            help='Specify one or more names for the tables to be created. If omitted, the filename (minus extension) or "stdin" will be used.')
        self.argparser.add_argument('--no-constraints', dest='no_constraints', action='store_true',
            help='Generate a schema without length limits or null checks. Useful when sampling big tables.')
        self.argparser.add_argument('--no-create', dest='no_create', action='store_true',
            help='Skip creating a table. Only valid when --insert is specified.')
        self.argparser.add_argument('--blanks', dest='blanks', action='store_true',
            help='Do not coerce empty strings to NULL values.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input.')
        self.argparser.add_argument('--db-schema', dest='db_schema',
            help='Optional name of database schema to create table(s) in.')

    def main(self):
        connection_string = self.args.connection_string
        do_insert = self.args.insert
        query = self.args.query

        self.input_files = []

        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        if self.args.table_names:
            table_names = self.args.table_names.split(',')
        else:
            table_names = []

        # If one or more filenames are specified, we need to add stdin ourselves (if available)
        if sys.stdin not in self.input_files:
            try:
                if not sys.stdin.isatty():
                    self.input_files.insert(0, sys.stdin)
            except:
                pass

        # Create an SQLite database in memory if no connection string is specified
        if query and not connection_string:
            connection_string = "sqlite:///:memory:"
            do_insert = True

        if self.args.dialect and connection_string:
            self.argparser.error('The --dialect option is only valid when --db is not specified.')

        if do_insert and not connection_string:
            self.argparser.error('The --insert option is only valid when --db is also specified.')

        if self.args.no_create and not do_insert:
            self.argparser.error('The --no-create option is only valid --insert is also specified.')

        # Establish database validity before reading CSV files
        if connection_string:
            try:
                engine, metadata = sql.get_connection(connection_string)
            except ImportError:
                raise ImportError('You don\'t appear to have the necessary database backend installed for connection string you\'re trying to use. Available backends include:\n\nPostgresql:\tpip install psycopg2\nMySQL:\t\tpip install MySQL-python\n\nFor details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at: \n\nhttp://www.sqlalchemy.org/docs/dialects/\n\n')
            conn = engine.connect()
            trans = conn.begin()

        for f in self.input_files:
            try:
                # Try to use name specified via --table
                table_name = table_names.pop(0)
            except IndexError:
                if f == sys.stdin:
                    table_name = "stdin"
                else:
                    # Use filename as table name
                    table_name = os.path.splitext(os.path.split(f.name)[1])[0]

            csv_table = table.Table.from_csv(
                f,
                name=table_name,
                snifflimit=self.args.snifflimit,
                blanks_as_nulls=(not self.args.blanks),
                infer_types=(not self.args.no_inference),
                no_header_row=self.args.no_header_row,
                **self.reader_kwargs
            )

            f.close()

            if connection_string:
                sql_table = sql.make_table(
                    csv_table,
                    table_name,
                    self.args.no_constraints,
                    self.args.db_schema,
                    metadata
                )

                # Create table
                if not self.args.no_create:
                    sql_table.create()

                # Insert data
                if do_insert and csv_table.count_rows() > 0:
                    insert = sql_table.insert()
                    headers = csv_table.headers()
                    conn.execute(insert, [dict(zip(headers, row)) for row in csv_table.to_rows()])

            # Output SQL statements
            else:
                sql_table = sql.make_table(csv_table, table_name, self.args.no_constraints)
                self.output_file.write('%s\n' % sql.make_create_table_statement(sql_table, dialect=self.args.dialect))

        if connection_string:
            if query:
                # Execute specified SQL queries
                queries = query.split(';')
                rows = None

                for q in queries:
                    if q:
                        rows = conn.execute(q)

                # Output result of last query as CSV
                try:
                    output = CSVKitWriter(self.output_file, **self.writer_kwargs)
                    if not self.args.no_header_row:
                        output.writerow(rows._metadata.keys)
                    for row in rows:
                        output.writerow(row)
                except AttributeError:
                    pass

            trans.commit()
            conn.close()

def launch_new_instance():
    utility = CSVSQL()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
