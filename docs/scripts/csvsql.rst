======
csvsql
======

Description
===========

Generate SQL statements for a CSV file or execute those statements directly on a database. In the latter case supports both creating tables and inserting data:

.. code-block:: none

   usage: csvsql [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                 [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                 [-S] [--blanks] [--null-value NULL_VALUES [NULL_VALUES ...]]
                 [--date-format DATE_FORMAT] [--datetime-format DATETIME_FORMAT]
                 [-H] [-K SKIP_LINES] [-v] [-l] [--zero] [-V]
                 [-i {firebird,mssql,mysql,oracle,postgresql,sqlite,sybase}]
                 [--db CONNECTION_STRING] [--query QUERIES] [--insert]
                 [--prefix PREFIX] [--before-insert BEFORE_INSERT]
                 [--after-insert AFTER_INSERT] [--tables TABLE_NAMES]
                 [--no-constraints] [--unique-constraint UNIQUE_CONSTRAINT]
                 [--no-create] [--create-if-not-exists] [--overwrite]
                 [--db-schema DB_SCHEMA] [-y SNIFF_LIMIT] [-I]
                 [--chunk-size CHUNK_SIZE]
                 [FILE [FILE ...]]

   Generate SQL statements for one or more CSV files, or execute those statements
   directly on a database, and execute one or more SQL queries.

   positional arguments:
     FILE                  The CSV file(s) to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     -i {mssql,mysql,oracle,postgresql,sqlite,duckdb,create,ingres}, --dialect {mssql,mysql,oracle,postgresql,sqlite,duckdb,create,ingres}
                           Dialect of SQL to generate. Cannot be used with --db.
     --db CONNECTION_STRING
                           If present, a SQLAlchemy connection string to use to
                           directly execute generated SQL on a database.
     --engine-option ENGINE_OPTION ENGINE_OPTION
                           A keyword argument to SQLAlchemy's create_engine(), as
                           a space-separated pair. This option can be specified
                           multiple times. For example: thick_mode True
     --query QUERIES       Execute one or more SQL queries delimited by --sql-
                           delimiter, and output the result of the last query as
                           CSV. QUERY may be a filename. --query may be specified
                           multiple times.
     --insert              Insert the data into the table. Requires --db.
     --prefix PREFIX       Add an expression following the INSERT keyword, like
                           OR IGNORE or OR REPLACE.
     --before-insert BEFORE_INSERT
                           Before the INSERT command, execute one or more SQL
                           queries delimited by --sql-delimiter. Requires
                           --insert.
     --after-insert AFTER_INSERT
                           After the INSERT command, execute one or more SQL
                           queries delimited by --sql-delimiter. Requires
                           --insert.
     --sql-delimiter SQL_DELIMITER
                           Delimiter separating SQL queries in --query, --before-
                           insert, and --after-insert.
     --tables TABLE_NAMES  A comma-separated list of names of tables to be
                           created. By default, the tables will be named after
                           the filenames without extensions or "stdin".
     --no-constraints      Generate a schema without length limits or null
                           checks. Useful when sampling big tables.
     --unique-constraint UNIQUE_CONSTRAINT
                           A column-separated list of names of columns to include
                           in a UNIQUE constraint.
     --no-create           Skip creating the table. Requires --insert.
     --create-if-not-exists
                           Create the table if it does not exist, otherwise keep
                           going. Requires --insert.
     --overwrite           Drop the table if it already exists. Requires
                           --insert. Cannot be used with --no-create.
     --db-schema DB_SCHEMA
                           Optional name of database schema to create table(s)
                           in.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           Limit CSV dialect sniffing to the specified number of
                           bytes. Specify "0" to disable sniffing entirely, or
                           "-1" to sniff the entire file.
     -I, --no-inference    Disable type inference (and --locale, --date-format,
                           --datetime-format, --no-leading-zeroes) when parsing
                           the input.
     --chunk-size CHUNK_SIZE
                           Chunk size for batch insert into the table. Requires
                           --insert.
     --min-col-len MIN_COL_LEN
                           The minimum length of text columns.
     --col-len-multiplier COL_LEN_MULTIPLIER
                           Multiply the maximum column length by this multiplier
                           to accommodate larger values in later runs.


See also: :doc:`../common_arguments`.

For information on connection strings and supported dialects refer to the `SQLAlchemy documentation <https://www.sqlalchemy.org/docs/dialects/>`_.

If you prefer not to enter your password in the connection string, store the password securely in a `PostgreSQL Password File <https://www.postgresql.org/docs/9.1/static/libpq-pgpass.html>`_, a `MySQL Options File <https://dev.mysql.com/doc/refman/5.7/en/option-files.html>`_ or similar files for other systems.

.. note::

    Using the :code:`--query` option may cause rounding (in Python 2) or introduce `Python floating point issues <https://docs.python.org/3/tutorial/floatingpoint.html>`_ (in Python 3).

.. note::

   If the CSV file was created from a JSON file using :doc:`in2csv`, remember to quote SQL columns properly. For example:

   .. code-block:: bash

      echo '{"a":{"b":"c"},"d":"e"}' | in2csv -f ndjson | csvsql --query 'SELECT "a/b" FROM stdin'

.. note::

    Alternatives to :doc:`csvsql` are `q <https://github.com/harelba/q>`_ and `textql <https://github.com/dinedal/textql>`_.

Examples
========

Generate SQL statements
-----------------------

Generate a statement in the PostgreSQL dialect:

.. code-block:: bash

   csvsql -i postgresql examples/realdata/FY09_EDU_Recipients_by_State.csv

Interact with a SQL database
----------------------------

Create a table and import data from the CSV directly into PostgreSQL:

.. code-block:: bash

   createdb test
   csvsql --db postgresql:///test --tables fy09 --insert examples/realdata/FY09_EDU_Recipients_by_State.csv

For large tables it may not be practical to process the entire table. One solution to this is to analyze a sample of the table. In this case it can be useful to turn off length limits and null checks with the :code:`--no-constraints` option:

.. code-block:: bash

   head -n 20 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsql --no-constraints --tables fy09

Create tables for an entire directory of CSVs and import data from those files directly into PostgreSQL:

.. code-block:: bash

   createdb test
   csvsql --db postgresql:///test --insert examples/*_converted.csv

If those CSVs have identical headers, you can import them into the same table by using :doc:`csvstack` first:

.. code-block:: bash

   createdb test
   csvstack examples/dummy?.csv | csvsql --db postgresql:///test --insert

Query and output CSV files using SQL
------------------------------------

You can use csvsql to "directly" query one or more CSV files. Please note that this will create an in-memory SQLite database, so it won't be very fast:

.. code-block:: bash

   csvsql --query  "SELECT m.usda_id, avg(i.sepal_length) AS mean_sepal_length FROM iris AS i JOIN irismeta AS m ON (i.species = m.species) GROUP BY m.species" examples/iris.csv examples/irismeta.csv

Group rows by one column:

.. code-block:: bash

   csvsql --query "SELECT * FROM 'dummy3' GROUP BY a" examples/dummy3.csv

Concatenate two columns:

.. code-block:: bash

   csvsql --query "SELECT a || b FROM 'dummy3'" --no-inference examples/dummy3.csv

If a column contains null values, you must ``COALESCE`` the column:

.. code-block:: bash

   csvsql --query "SELECT a || COALESCE(b, '') FROM 'sort_ints_nulls'" --no-inference examples/sort_ints_nulls.csv

The ``UPDATE`` SQL statement produces no output. Remember to ``SELECT`` the columns and rows you want:

.. code-block:: bash

   csvsql --query "UPDATE 'dummy3' SET a = 'foo'; SELECT * FROM 'dummy3'" examples/dummy3.csv
