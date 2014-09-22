========
csvclean
========

Description
===========

Cleans a CSV file of common syntax errors. Outputs [basename]_out.csv and [basename]_err.csv, the former containing all valid rows and the latter containing all error rows along with line numbers and descriptions::

    usage: csvclean [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p` ESCAPECHAR] [-e ENCODING] [-n]
                    [FILE]

    Fix common syntax errors in a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --dry-run         If this argument is present, no output will be
                            created. Information about what would have been done
                            will be printed to STDERR.

See also: :doc:`../common_arguments`.

Examples
========

Test a file with known bad rows::

    $ csvclean -n examples/bad.csv

    Line 3: Expected 3 columns, found 4 columns
    Line 4: Expected 3 columns, found 2 columns
