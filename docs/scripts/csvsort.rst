=======
csvsort
=======

Description
===========

Sort CSV files. Like unix "sort" command, but for tabular data::

    usage: csvsort [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p` ESCAPECHAR] [-e ENCODING] [-n] [-c COLUMNS] [-r]
                   [FILE]

    Sort CSV files. Like unix "sort" command, but for tabular data.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
                            Specify the encoding the input file.
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            sort by. Defaults to all columns.
      -r, --reverse         Sort in descending order.
      --no-inference        Disable type inference when parsing the input.
 
See also: :doc:`../common_arguments`.

Examples
========

Sort the veteran's education benefits table by the "TOTAL" column::

    $ cat examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsort -c 9

View the five states with the most individuals claiming veteran's education benefits::

    $ cat examples/realdata/FY09_EDU_Recipients_by_State.csv | csvcut -c 1,9 | csvsort -r -c 2 | head -n 5
