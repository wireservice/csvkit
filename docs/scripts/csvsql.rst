======
csvsql
======

Description
===========

Generate SQL statements for a CSV file or execute those statements directly on a database. In the latter case supports both creating tables and inserting data::

    usage: csvsql [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-H] [-v]
                  [--zero] [-y SNIFFLIMIT]
                  [-i {firebird,maxdb,informix,mssql,oracle,sybase,sqlite,access,mysql,postgresql}]
                  [--db CONNECTION_STRING] [--query QUERY] [--insert]
                  [--tables TABLE_NAMES] [--no-constraints] [--no-create]
                  [--blanks] [--no-inference] [--db-schema DB_SCHEMA]
                  [FILE [FILE ...]]

    Generate SQL statements for one or more CSV files, or execute those
    statements directly on a database, and execute one or more SQL queries.

    positional arguments:
      FILE                  The CSV file(s) to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
      -i {firebird,maxdb,informix,mssql,oracle,sybase,sqlite,access,mysql,postgresql}, --dialect {firebird,maxdb,informix,mssql,oracle,sybase,sqlite,access,mysql,postgresql}
                            Dialect of SQL to generate. Only valid when --db is
                            not specified.
      --db CONNECTION_STRING
                            If present, a sqlalchemy connection string to use to
                            directly execute generated SQL on a database.
      --query QUERY         Execute one or more SQL queries delimited by ";" and
                            output the result of the last query as CSV.
      --insert              In addition to creating the table, also insert the
                            data into the table. Only valid when --db is
                            specified.
      --tables TABLE_NAMES  Specify the names of the tables to be created. By
                            default, the tables will be named after the
                            filenames without extensions or "stdin".
      --no-constraints      Generate a schema without length limits or null
                            checks. Useful when sampling big tables.
      --no-create           Skip creating a table. Only valid when --insert is
                            specified.
      --blanks              Do not coerce empty strings to NULL values.
      --no-inference        Disable type inference when parsing the input.
      --db-schema DB_SCHEMA
                            Optional name of database schema to create table(s)
                            in.

See also: :doc:`../common_arguments`.

For information on connection strings and supported dialects refer to the `SQLAlchemy documentation <http://www.sqlalchemy.org/docs/dialects/>`_.


.. note::

    Using the ``--query`` option may cause rounding (in Python 2) or introduce [Python floating point issues](https://docs.python.org/3.4/tutorial/floatingpoint.html) (in Python 3).

Examples
========

Generate a statement in the PostgreSQL dialect::

    csvsql -i postgresql examples/realdata/FY09_EDU_Recipients_by_State.csv

Create a table and import data from the CSV directly into PostgreSQL::

    createdb test
    csvsql --db postgresql:///test --table fy09 --insert examples/realdata/FY09_EDU_Recipients_by_State.csv

For large tables it may not be practical to process the entire table. One solution to this is to analyze a sample of the table. In this case it can be useful to turn off length limits and null checks with the ``no-constraints`` option::

    head -n 20 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsql --no-constraints --table fy09

Create tables for an entire folder of CSVs and import data from those files directly into PostgreSQL::

    createdb test
    csvsql --db postgresql:///test --insert examples/*_converted.csv

If those CSVs have identical headers, you can import them into the same table by using :doc:`csvstack` first::

    createdb test
    csvstack examples/dummy?.csv | csvsql --db postgresql:///test --insert

Group rows by one column::

    csvsql --query "select * from 'dummy3' group by a" examples/dummy3.csv

You can also use CSVSQL to "directly" query one or more CSV files. Please note that this will create an in-memory SQL database, so it won't be very fast::

    csvsql --query  "select m.usda_id, avg(i.sepal_length) as mean_sepal_length from iris as i join irismeta as m on (i.species = m.species) group by m.species" examples/iris.csv examples/irismeta.csv
