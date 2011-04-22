======
csvcut
======

Description
===========

Filters and truncates CSV files. Like unix "cut" command, but for tabular data::

    usage: csvcut [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p` ESCAPECHAR] [-e ENCODING] [-n] [-c COLUMNS] [-s] [-l]
                  [FILE]

    Filter and truncate CSV files. Like unix "cut" command, but for tabular data.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be extracted. Defaults to all columns.
      -l, --linenumbers     Insert a column of line numbers at the front of the
                            output. Useful when piping to grep or as a simple
                            primary key.

Note that csvcut does not include row slicing or filtering, for this you should pipe data to grep. See :doc:`unix_tools`.

Also see: :doc:`common_arguments`.

Examples
========

Print the indices and names of all columns::

    $ csvcut -n examples/testfixed_converted.csv

      1: text
      2: date
      3: integer
      4: boolean
      5: float
      6: time
      7: datetime
      8: empty_column

Extract the first and third columns::

    $ csvcut -c 1,3 examples/testfixed_converted.csv

Extract columns named "integer" and "date"::

    $ csvcut -c integer,date examples/testfixed_converted.csv
