======
csvcut
======

Description
===========

Filters and truncates CSV files. Like the Unix "cut" command, but for tabular data:

.. code-block:: none

   usage: csvcut [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3,4,5}] [-b]
                 [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                 [-K SKIP_LINES] [-v] [--output-compression {gzip,bz2,zst}]
                 [--compression-level {1,2,3,4,5,6,7,8,9}] [-l] [--add-bom]
                 [--zero] [-V] [-n] [-c COLUMNS] [-C NOT_COLUMNS] [-x]
                 [--ignore-unknown-columns]
                 [FILE]

   Filter and truncate CSV files. Like the Unix "cut" command, but for tabular
   data.

   positional arguments:
     FILE                  CSV file to read. Named files are decompressed by
                           extension: gzip (.gz), bzip2 (.bz2), xz (.xz), or
                           Zstandard (.zst, requires the optional zstandard
                           package).
                           Omit FILE or use "-" to read uncompressed CSV from
                           stdin.

   optional arguments:
     -h, --help            show this help message and exit
     --output-compression {gzip,bz2,zst}
                           Compress standard output using gzip, bzip2 or
                           Zstandard (requires the zstandard package).
     --compression-level {1,2,3,4,5,6,7,8,9}
                           Set the compression level (default: 9 for gzip/bz2, 3
                           for zst). Requires --output-compression.
     -n, --names           Display column names and indices from the input CSV
                           and exit.
     -c COLUMNS, --columns COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to be extracted, e.g. "1,id,3-5". Defaults to
                           all columns.
     -C NOT_COLUMNS, --not-columns NOT_COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to be excluded, e.g. "1,id,3-5". Defaults to no
                           columns. Ignores unknown columns.
     -x, --delete-empty-rows
                           After cutting, delete rows which are completely empty.
     --ignore-unknown-columns
                           Ignore identifiers in --columns (-c) that do not match
                           a column in the input, instead of erroring.

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
