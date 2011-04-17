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

Examples
========

Generate a statement in the postgresql dialect::

    csvsql -i postgresql examples/testfixed_converted.csv
