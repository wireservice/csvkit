=======
csvgrep
=======

Description
===========

Filter tabular data to only those rows where certain columns contain a given value or match a regular expression::

    usage: csvgrep [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v] [-l]
                   [--zero] [-n] [-c COLUMNS] [-m PATTERN] [-r REGEX]
                   [-f MATCHFILE] [-i]
                   [FILE]

    Search CSV files. Like the Unix "grep" command, but for tabular data.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be searched.
      -m PATTERN, --match PATTERN
                            The string to search for.
      -r REGEX, --regex REGEX
                            If specified, must be followed by a regular expression
                            which will be tested against the specified columns.
      -f MATCHFILE, --file MATCHFILE
                            If specified, must be the path to a file. For each
                            tested row, if any line in the file (stripped of line
                            separators) is an exact match for the cell value, the
                            row will pass.
      -i, --invert-match    If specified, select non-matching instead of matching
                            rows.

See also: :doc:`../common_arguments`.

NOTE: Even though '-m', '-r', and '-f' are listed as "optional" arguments, you must specify one of them.

Examples
========

Search for the row relating to Illinois::

    csvgrep -c 1 -m ILLINOIS examples/realdata/FY09_EDU_Recipients_by_State.csv

Search for rows relating to states with names beginning with the letter "I"::

    csvgrep -c 1 -r "^I" examples/realdata/FY09_EDU_Recipients_by_State.csv

