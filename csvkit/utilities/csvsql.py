#!/usr/bin/env python

import os
from pkg_resources import iter_entry_points
import sys

import agate
import agatesql  # noqa
from sqlalchemy import create_engine, dialects

from csvkit.cli import CSVKitUtility

DIALECTS = dialects.__all__ + tuple(e.name for e in iter_entry_points('sqlalchemy.dialects'))


class CSVSQL(CSVKitUtility):
    description = 'Generate SQL statements for one or more CSV files, or execute those statements directly on a database, and execute one or more SQL queries.'
    override_flags = ['l', 'f']

    def add_arguments(self):

        self.argparser.add_argument(metavar="FILE", nargs='*', dest='input_paths', default=['-'],
                                    help='The CSV file(s) to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-i', '--dialect', dest='dialect', choices=DIALECTS,
                                    help='Dialect of SQL to generate. Only valid when --db is not specified.')
        self.argparser.add_argument('--db', dest='connection_string',
                                    help='If present, a sqlalchemy connection string to use to directly execute generated SQL on a database.')
        self.argparser.add_argument('--query', default=None,
                                    help='Execute one or more SQL queries delimited by ";" and output the result of the last query as CSV.')
        self.argparser.add_argument('--insert', dest='insert', action='store_true',
                                    help='In addition to creating the table, also insert the data into the table. Only valid when --db is specified.')
        self.argparser.add_argument('--tables', dest='table_names',
                                    help='Specify the names of the tables to be created. By default, the tables will be named after the filenames without extensions or "stdin".')
        self.argparser.add_argument('--no-constraints', dest='no_constraints', action='store_true',
                                    help='Generate a schema without length limits or null checks. Useful when sampling big tables.')
        self.argparser.add_argument('--no-create', dest='no_create', action='store_true',
                                    help='Skip creating a table. Only valid when --insert is specified.')
        self.argparser.add_argument('--blanks', dest='blanks', action='store_true',
                                    help='Do not coerce empty strings to NULL values.')
        self.argparser.add_argument('--db-schema', dest='db_schema',
                                    help='Optional name of database schema to create table(s) in.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')

    def main(self):
        self.input_files = []
        self.connection = None
        self.table_names = []

        if self.args.table_names:
            self.table_names = self.args.table_names.split(',')

        # Create an SQLite database in memory if no connection string is specified
        if self.args.query and not self.args.connection_string:
            self.args.connection_string = "sqlite:///:memory:"
            self.args.insert = True

        if self.args.dialect and self.args.connection_string:
            self.argparser.error('The --dialect option is only valid when neither --db nor --query are specified.')

        if self.args.insert and not self.args.connection_string:
            self.argparser.error('The --insert option is only valid when either --db or --query is specified.')

        if self.args.no_create and not self.args.insert:
            self.argparser.error('The --no-create option is only valid --insert is also specified.')

        # Lazy open files
        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        # Establish database validity before reading CSV files
        if self.args.connection_string:
            try:
                engine = create_engine(self.args.connection_string)
            except ImportError:
                raise ImportError('You don\'t appear to have the necessary database backend installed for connection string you\'re trying to use. Available backends include:\n\nPostgresql:\tpip install psycopg2\nMySQL:\t\tpip install MySQL-python\n\nFor details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at: \n\nhttp://www.sqlalchemy.org/docs/dialects/\n\n')

            self.connection = engine.connect()

        try:
            self._failsafe_main()
        finally:
            for f in self.input_files:
                f.close()

            if self.connection:
                self.connection.close()

    def _failsafe_main(self):
        """
        Inner main function. If anything fails in here, file handles and
        database connections will be safely closed.
        """
        if self.connection:
            transaction = self.connection.begin()

        for f in self.input_files:
            try:
                # Try to use name specified via --table
                table_name = self.table_names.pop(0)
            except IndexError:
                if f == sys.stdin:
                    table_name = "stdin"
                else:
                    # Use filename as table name
                    table_name = os.path.splitext(os.path.split(f.name)[1])[0]

            table = None

            try:
                table = agate.Table.from_csv(
                    f,
                    sniff_limit=self.args.sniff_limit,
                    header=not self.args.no_header_row,
                    column_types=self.get_column_types(),
                    **self.reader_kwargs
                )
            except StopIteration:
                # Catch cases where no table data was provided and fall through
                # to query logic
                continue

            if table:
                if self.connection:
                    table.to_sql(
                        self.connection,
                        table_name,
                        create=(not self.args.no_create),
                        insert=(self.args.insert and len(table.rows) > 0),
                        constraints=()
                    )

                # Output SQL statements
                else:
                    statement = table.to_sql_create_statement(
                        table_name,
                        dialect=self.args.dialect
                    )

                    self.output_file.write('%s\n' % statement)

        if self.connection:
            if self.args.query:
                # Execute the specified SQL queries
                queries = self.args.query.split(';')
                rows = None

                for q in queries:
                    if q:
                        rows = self.connection.execute(q)

                # Output the result of the last query as CSV
                try:
                    output = agate.csv.writer(self.output_file, **self.writer_kwargs)
                    output.writerow(rows._metadata.keys)
                    for row in rows:
                        output.writerow(row)
                except AttributeError:
                    pass

            transaction.commit()


def launch_new_instance():
    utility = CSVSQL()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
