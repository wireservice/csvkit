========
csvclean
========

Description
===========

Cleans a CSV file of common syntax errors:

* reports rows that have a different number of columns than the header row
* attempts to correct the CSV by joining short rows into a single row

Note that every csvkit tool does the following:

* removes optional quote characters, unless the `--quoting` (`-u`) option is set to change this behavior
* changes the field delimiter to a comma, if the input delimiter is set with the `--delimiter` (`-d`) or `--tabs` (`-t`) options
* changes the record delimiter to a line feed
* changes the quote character to a double-quotation mark, if the character is set with the `--quotechar` (`-q`) option
* changes the character encoding to UTF-8, if the input encoding is set with the `--encoding` (`-e`) option

Outputs [basename]_out.csv and [basename]_err.csv, the former containing all valid rows and the latter containing all error rows along with line numbers and descriptions::

    usage: csvclean [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                    [-K SKIP_LINES] [-v] [-l] [--zero] [-V] [-n]
                    [FILE]

    Fix common errors in a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --dry-run         Do not create output files. Information about what
                            would have been done will be printed to STDERR.

See also: :doc:`../common_arguments`.

Examples
========

Test a file with known bad rows::

    csvclean -n examples/bad.csv

    Line 1: Expected 3 columns, found 4 columns
    Line 2: Expected 3 columns, found 2 columns
