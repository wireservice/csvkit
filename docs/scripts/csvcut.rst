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

Note that csvcut does not include row filtering, for this you should pipe data to :doc:`csvgrep`.

Also see: :doc:`common_arguments`.

Examples
========

Print the indices and names of all columns::

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

Extract the first and third columns::

    $ csvcut -c 1,3 examples/realdata/FY09_EDU_Recipients_by_State.csv

Extract columns named "TOTAL" and "State Name" (in that order)::

    $ csvcut -c TOTAL,"State Name" examples/realdata/FY09_EDU_Recipients_by_State.csv

