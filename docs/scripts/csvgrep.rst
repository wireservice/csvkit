=======
csvgrep
=======

Description
===========

Filter tabular data to only those rows where certain columns contain a given value or match a regular expression:

.. code-block:: none

   usage: csvgrep [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3,4,5}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                  [-K SKIP_LINES] [-v] [--output-compression {gzip,bz2,zst}]
                  [--compression-level {1,2,3,4,5,6,7,8,9}] [-l] [--add-bom]
                  [--zero] [-V] [-n] [-c COLUMNS] [-m PATTERN] [-r REGEX]
                  [-f MATCHFILE] [-i] [-a]
                  [FILE]

   Search CSV files. Like the Unix "grep" command, but for tabular data.

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
                           ranges to be searched, e.g. "1,id,3-5".
     -m PATTERN, --match PATTERN
                           A string to search for.
     -r REGEX, --regex REGEX
                           A regular expression to match.
     -f, --file MATCHFILE  A plain-text match file. A row matches if its cell
                           value exactly matches any line in the file (excluding
                           the line separator).
     -i, --invert-match    Select non-matching rows, instead of matching rows.
     -a, --any-match       Select rows in which any column matches, instead of
                           all columns.

See also: :doc:`../common_arguments`.

NOTE: Even though '-m', '-r', and '-f' are listed as "optional" arguments, you must specify one of them.

Examples
========

Search for the row relating to Illinois:

.. code-block:: bash

   csvgrep -c 1 -m ILLINOIS examples/realdata/FY09_EDU_Recipients_by_State.csv

Search for rows relating to states with names beginning with the letter "I":

.. code-block:: bash

   csvgrep -c 1 -r "^I" examples/realdata/FY09_EDU_Recipients_by_State.csv

Search for rows that do not contain an empty state cell:

.. code-block:: bash

   csvgrep -c 1 -r "^$" -i examples/realdata/FY09_EDU_Recipients_by_State.csv

Perform a case-insensitive search:

.. code-block:: bash

   csvgrep -c 1 -r "(?i)illinois" examples/realdata/FY09_EDU_Recipients_by_State.csv

Remove comment rows:

.. code-block:: bash

   printf "a,b\n1,2\n# a comment\n3,4" | csvgrep --invert-match -c1 -r '^#'

Get the indices of the columns that contain matching text (``\x1e`` is the `Record Separator (RS) character <https://en.wikipedia.org/wiki/C0_and_C1_control_codes#Field_separators>`_):

.. code-block::

   csvgrep -m 22 -a -c 1- examples/realdata/FY09_EDU_Recipients_by_State.csv | csvformat -M $'\x1e' | xargs -d $'\x1e' -n1 sh -c 'echo $0 | csvcut -n' | grep 22

.. note::

   This last example is not performant.
