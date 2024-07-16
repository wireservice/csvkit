=======
sql2csv
=======

Description
===========

Executes arbitrary commands against a SQL database and outputs the results as a CSV:

.. code-block:: none

   usage: sql2csv [-h] [-v] [-l] [-V] [--db CONNECTION_STRING] [--query QUERY]
                  [-e ENCODING] [-H]
                  [FILE]

   Execute a SQL query on a database and output the result to a CSV file.

   positional arguments:
     FILE                  The file to use as the SQL query. If FILE and --query
                           are omitted, the query is piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     --db CONNECTION_STRING
                           A SQLAlchemy connection string to connect to a
                           database.
     --engine-option ENGINE_OPTION ENGINE_OPTION
                           A keyword argument to SQLAlchemy's create_engine(), as
                           a space-separated pair. This option can be specified
                           multiple times. For example: thick_mode True
     --execution-option EXECUTION_OPTION EXECUTION_OPTION
                           A keyword argument to SQLAlchemy's
                           execution_options(), as a space-separated pair. This
                           option can be specified multiple times. For example:
                           stream_results True
     --query QUERY         The SQL query to execute. Overrides FILE and STDIN.
     -e ENCODING, --encoding ENCODING
                           Specify the encoding of the input query file.
     -H, --no-header-row   Do not output column names.

Examples
========

Load sample data into a table using :doc:`csvsql` and then query it using `sql2csv`:

.. code-block:: bash

   csvsql --db "sqlite:///dummy.db" --tables "test" --insert examples/dummy.csv
   sql2csv --db "sqlite:///dummy.db" --query "select * from test"

Load data about financial aid recipients into PostgreSQL. Then find the three states that received the most, while also filtering out empty rows:

.. code-block:: bash

   createdb recipients
   csvsql --db "postgresql:///recipients" --tables "fy09" --insert examples/realdata/FY09_EDU_Recipients_by_State.csv
   sql2csv --db "postgresql:///recipients" --query "select * from fy09 where \"State Name\" != '' order by fy09.\"TOTAL\" limit 3"

You can even use it as a simple SQL calculator (in this example an in-memory SQLite database is used as the default):

.. code-block:: bash

   sql2csv --query "select 300 * 47 % 14 * 27 + 7000"

The connection string `accepts parameters <https://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#engine-creation-api>`_. For example, to set the encoding of a MySQL database:

.. code-block:: bash

   sql2csv --db 'mysql://user:pass@host/database?charset=utf8' --query "SELECT myfield FROM mytable"
