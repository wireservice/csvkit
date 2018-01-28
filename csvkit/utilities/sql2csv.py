#!/usr/bin/env python

import agate
from sqlalchemy import create_engine

from csvkit.cli import CSVKitUtility


class SQL2CSV(CSVKitUtility):
    description = 'Execute an SQL query on a database and output the result to a CSV file.'
    # Overrides all flags except --linenumbers, --verbose, --version.
    override_flags = 'f,b,d,e,H,K,L,p,q,S,t,u,z,blanks,date-format,datetime-format,zero'.split(',')

    def add_arguments(self):
        self.argparser.add_argument('--db', dest='connection_string', default='sqlite://',
                                    help='An sqlalchemy connection string to connect to a database.',)
        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The file to use as SQL query. If both FILE and QUERY are omitted, query will be read from STDIN.')
        self.argparser.add_argument('--query',
                                    help="The SQL query to execute. If specified, it overrides FILE and STDIN.")
        self.argparser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                                    help='Specify the encoding of the input query file.')
        self.argparser.add_argument('-H', '--no-header-row', dest='no_header_row', action='store_true',
                                    help='Do not output column names.')

        self.argparser.set_defaults(
            delimiter=None,
            doublequote=None,
            escapechar=None,
            encoding='utf-8',
            field_size_limit=None,
            quotechar=None,
            quoting=None,
            skipinitialspace=None,
            tabs=None,
        )

    def main(self):
        if self.additional_input_expected() and not self.args.query:
            self.argparser.error('You must provide an input file or piped data.')

        try:
            engine = create_engine(self.args.connection_string)
        except ImportError:
            raise ImportError("You don't appear to have the necessary database backend installed for connection "
                              "string you're trying to use. Available backends include:\n\nPostgreSQL:\tpip install "
                              "psycopg2\nMySQL:\t\tpip install MySQL-python\n\nFor details on connection strings and "
                              "other backends, please see the SQLAlchemy documentation on dialects at:\n\n"
                              "http://www.sqlalchemy.org/docs/dialects/\n\n")

        connection = engine.connect()

        if self.args.query:
            query = self.args.query.strip()
        else:
            query = ""

            self.input_file = self._open_input_file(self.args.input_path)

            for line in self.input_file:
                query += line

            self.input_file.close()

        rows = connection.execution_options(no_parameters=True).execute(query)
        output = agate.csv.writer(self.output_file, **self.writer_kwargs)

        if rows.returns_rows:
            if not self.args.no_header_row:
                output.writerow(rows._metadata.keys)

            for row in rows:
                output.writerow(row)

        connection.close()


def launch_new_instance():
    utility = SQL2CSV()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
