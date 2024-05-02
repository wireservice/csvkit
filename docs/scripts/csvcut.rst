======
csvcut
======

Description
===========

Filters and truncates CSV files. Like the Unix "cut" command, but for tabular data:

.. code-block:: none

   usage: csvcut [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                 [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                 [-K SKIP_LINES] [-v] [-l] [--zero] [-V] [-n] [-c COLUMNS]
                 [-C NOT_COLUMNS] [-x]
                 [FILE]

   Filter and truncate CSV files. Like the Unix "cut" command, but for tabular
   data.

   positional arguments:
     FILE                  The CSV file to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     -n, --names           Display column names and indices from the input CSV
                           and exit.
     -c COLUMNS, --columns COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to be extracted, e.g. "1,id,3-5". Defaults to
                           all columns.
     -C NOT_COLUMNS, --not-columns NOT_COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to be excluded, e.g. "1,id,3-5". Defaults to no
                           columns.
     -x, --delete-empty-rows
                           After cutting, delete rows which are completely empty.

See also: :doc:`../common_arguments`.

.. note::

    csvcut does not implement row filtering, for this you should pipe data to :doc:`csvgrep`.

.. note::

    If a data row is longer than the header row, its additional columns are truncated.

Examples
========

Print columns
-------------

Print the indices and names of all columns:

.. code-block:: console

   $ csvcut -n examples/realdata/FY09_EDU_Recipients_by_State.csv 
     1: State Name
     2: State Abbreviate
     3: Code
     4: Montgomery GI Bill-Active Duty
     5: Montgomery GI Bill- Selective Reserve
     6: Dependents' Educational Assistance
     7: Reserve Educational Assistance Program
     8: Post-Vietnam Era Veteran's Educational Assistance Program
     9: TOTAL
    10: 

Print only the names of all columns, by removing the indices with the :code:`cut` command:

.. code-block:: console

   $ csvcut -n examples/realdata/FY09_EDU_Recipients_by_State.csv | cut -c6-
   State Name
   State Abbreviate
   Code
   Montgomery GI Bill-Active Duty
   Montgomery GI Bill- Selective Reserve
   Dependents' Educational Assistance
   Reserve Educational Assistance Program
   Post-Vietnam Era Veteran's Educational Assistance Program
   TOTAL

Extract columns
---------------

Extract the first and third columns:

.. code-block:: bash

   csvcut -c 1,3 examples/realdata/FY09_EDU_Recipients_by_State.csv

Extract columns named "TOTAL" and "State Name" (in that order):

.. code-block:: bash

   csvcut -c TOTAL,"State Name" examples/realdata/FY09_EDU_Recipients_by_State.csv

Extract a column that may not exist in all files:

.. code-block:: bash

   echo d, | csvjoin examples/dummy.csv - | csvcut -c d
    echo d, | csvjoin examples/join_no_header_row.csv - | csvcut -c d

Other
-----

Add line numbers to a file, making no other changes:

.. code-block:: bash

   csvcut -l examples/realdata/FY09_EDU_Recipients_by_State.csv

Display a column's unique values:

.. code-block:: bash

   csvcut -c 1 examples/realdata/FY09_EDU_Recipients_by_State.csv | sed 1d | sort | uniq

Or:

.. code-block:: bash

   csvcut -c 1 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsql --query 'SELECT DISTINCT("State Name") FROM stdin'
