#!/usr/bin/env python

from argparse import FileType
import sys

import agate
from sqlalchemy import create_engine

from csvkit.cli import CSVKitUtility


class SQL2CSV(CSVKitUtility):
    description = 'Execute an SQL query on a database and output the result to a CSV file.'
    override_flags = 'f,b,d,e,H,p,q,S,t,u,z,zero'.split(',')

    def add_arguments(self):
        self.argparser.add_argument('--db', dest='connection_string', default='sqlite://',
                                    help='An sqlalchemy connection string to connect to a database.',)
        self.argparser.add_argument('file', metavar="FILE", nargs='?', type=FileType('rt'), default=sys.stdin,
                                    help='The file to use as SQL query. If both FILE and QUERY are omitted, query will be read from STDIN.')
        self.argparser.add_argument('--query', default=None,
                                    help="The SQL query to execute. If specified, it overrides FILE and STDIN.")
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
        try:
            engine = create_engine(self.args.connection_string)
        except ImportError:
            raise ImportError('You don\'t appear to have the necessary database backend installed for connection string you\'re trying to use. Available backends include:\n\nPostgresql:\tpip install psycopg2\nMySQL:\t\tpip install MySQL-python\n\nFor details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at: \n\nhttp://www.sqlalchemy.org/docs/dialects/\n\n')

        connection = engine.connect()

        if self.args.query:
            query = self.args.query.strip()
        else:
            query = ""

            for line in self.args.file:
                query += line

        # Must escape '%'.
        # @see https://github.com/wireservice/csvkit/issues/440
        # @see https://bitbucket.org/zzzeek/sqlalchemy/commits/5bc1f17cb53248e7cea609693a3b2a9bb702545b
        rows = connection.execute(query.replace('%', '%%'))
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
