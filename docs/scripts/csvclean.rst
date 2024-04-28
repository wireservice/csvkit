========
csvclean
========

Description
===========

Cleans a CSV file of common syntax errors:

* reports rows that have a different number of columns than the header row
* attempts to correct the CSV by merging short rows into a single row

Note that every csvkit tool does the following:

* removes optional quote characters, unless the `--quoting` (`-u`) option is set to change this behavior
* changes the field delimiter to a comma, if the input delimiter is set with the `--delimiter` (`-d`) or `--tabs` (`-t`) options
* changes the record delimiter to a line feed (LF or ``\n``)
* changes the quote character to a double-quotation mark, if the character is set with the `--quotechar` (`-q`) option
* changes the character encoding to UTF-8, if the input encoding is set with the `--encoding` (`-e`) option

All valid rows are written to standard output, and all error rows along with line numbers and descriptions are written to standard error. If there are error rows, the exit code will be 1::

.. code-block:: none

   usage: csvclean [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                   [-K SKIP_LINES] [-v] [-l] [--zero] [-V]
                   [FILE]

   Fix common errors in a CSV file.

   positional arguments:
     FILE                  The CSV file to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit

See also: :doc:`../common_arguments`.

Examples
========

Test a file with known bad rows:

.. code-block:: console

   $ csvclean examples/bad.csv 2> errors.csv
   column_a,column_b,column_c
   0,mixed types.... uh oh,17
   $ cat errors.csv
   line_number,msg,column_a,column_b,column_c
   1,"Expected 3 columns, found 4 columns",1,27,,I'm too long!
   2,"Expected 3 columns, found 2 columns",,I'm too short!

To change the line ending from line feed (LF or ``\n``) to carriage return and line feed (CRLF or ``\r\n``) use:

.. code-block:: bash

   csvformat -M $'\r\n' examples/dummy.csv
