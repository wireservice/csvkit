=========
csvformat
=========

Description
===========

Convert a CSV file to a custom output format.::

    usage: csvformat [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                     [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v]
                     [-D OUT_DELIMITER] [-T] [-Q OUT_QUOTECHAR] [-U {0,1,2,3}]
                     [-B] [-P OUT_ESCAPECHAR] [-M OUT_LINETERMINATOR]
                     [FILE]

    Convert a CSV file to a custom output format.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -D OUT_DELIMITER, --out-delimiter OUT_DELIMITER
                            Delimiting character of the output CSV file.
      -T, --out-tabs        Specifies that the output CSV file is delimited with
                            tabs. Overrides "-D".
      -Q OUT_QUOTECHAR, --out-quotechar OUT_QUOTECHAR
                            Character used to quote strings in the output CSV
                            file.
      -U {0,1,2,3}, --out-quoting {0,1,2,3}
                            Quoting style used in the output CSV file. 0 = Quote
                            Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 =
                            Quote None.
      -B, --out-no-doublequote
                            Whether or not double quotes are doubled in the output
                            CSV file.
      -P OUT_ESCAPECHAR, --out-escapechar OUT_ESCAPECHAR
                            Character used to escape the delimiter in the output
                            CSV file if --quoting 3 ("Quote None") is specified
                            and to escape the QUOTECHAR if --no-doublequote is not
                            specified.
      -M OUT_LINETERMINATOR, --out-lineterminator OUT_LINETERMINATOR
                            Character used to terminate lines in the output CSV
                            file.

See also: :doc:`../common_arguments`.

Examples
========

Convert a comma-separated file to a pipe-delimited file::

    csvformat -D "|" examples/dummy.csv

Convert to carriage return line-endings::

    csvformat -M $"\r" examples/dummy.csv

