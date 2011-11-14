======
csvsql
======

Description
===========

Generate SQL statements for a CSV file or create execute those statements directly on a database. In the latter case supports both creating tables and inserting data.::

    usage: csvsql [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-v]
                  [-y SNIFFLIMIT]
                  [-i {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}]
                  [--db CONNECTION_STRING] [--insert]
                  [FILE]

    Generate SQL statements for a CSV file or create execute those statements
    directly on a database.

    Generate a SQL CREATE TABLE statement for a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes.
      -i {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}, --dialect {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}
                            Dialect of SQL to generate. Only valid when --db is
                            not specified.
      --db CONNECTION_STRING
                            If present, a sqlalchemy connection string to use to
                            directly execute generated SQL on a database.
      --insert              In addition to creating the table, also insert the
                            data into the table. Only valid when --db is
                            specified.
      --table TABLE_NAME    Specify a name for the table to be created. If
                            omitted, the filename (minus extension) will be used.

Also see: :doc:`common_arguments`.

For information on connection strings and supported dialects refer to the `SQLAlchemy documentation <http://www.sqlalchemy.org/docs/dialects/>`_.

Examples
========

Generate a statement in the PostgreSQL dialect::

    $ csvsql -i postgresql  examples/realdata/FY09_EDU_Recipients_by_State.csv

Create a table and import data from the CSV directly into Postgres::

    $ createdb test
    $ csvsql --db postgresql:///test --name fy09 --insert examples/realdata/FY09_EDU_Recipients_by_State.csv

