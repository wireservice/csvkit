======
csvsql
======

Description
===========

Generates a SQL "CREATE TABLE" statement for a given CSV file. Supports a variety of SQL dialects::

    usage: csvsql [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p` ESCAPECHAR] [-e ENCODING]
                  [-i {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}]
                  [FILE]

    Generate a SQL CREATE TABLE statement for a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -i {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}, --dialect {access,sybase,sqlite,informix,firebird,mysql,oracle,maxdb,postgresql,mssql}
                            Dialect of SQL to generate.
      --inserts             In additional to generating a CREATE TABLE statement,
                            also generate an INSERT statement for each row of
                            data.                     

Also see: :doc:`common_arguments`.

Examples
========

Generate a statement in the postgresql dialect::

    $ csvsql -i postgresql  examples/realdata/FY09_EDU_Recipients_by_State.csv

Generate create and insert statements for postgres, then actually run those statements to import all data into a test database::

    $ csvsql -i postgresql --inserts examples/realdata/FY09_EDU_Recipients_by_State.csv | psql -d test
