=======
csvjoin
=======

Description
===========

Filter tabular data to only those rows where certain columns contain a given value or match a regular expression::

    usage: csvgrep [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-e ENCODING] [-l] [-n] [-c COLUMNS] [-r]
                   [FILE] [PATTERN]

    Like the unix "grep" command, but for tabular data.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.
      PATTERN               The pattern to search for.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be searched.
      -r, --regex           If specified, the search pattern will be treated as a
                            regular expression.

Also see: :doc:`common_arguments`.

Examples
========

Grep examples coming soon...

