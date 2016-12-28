=======
csvstat
=======

Description
===========

Prints descriptive statistics for all columns in a CSV file. Will intelligently determine the type of each column and then print analysis relevant to that type (ranges for dates, mean and median for integers, etc.)::

    usage: csvstat [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                   [-v] [--zero] [--csv] [-n] [-c COLUMNS] [--type] [--nulls]
                   [--unique] [--min] [--max] [--sum] [--mean] [--median]
                   [--stdev] [--len] [--freq] [--count] [-y SNIFF_LIMIT]
                   [FILE]

    Print descriptive statistics for each column in a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      --csv                 Output results as a CSV, rather than text.
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be examined. Defaults to all columns.
      --type                Only output data type.
      --nulls               Only output whether columns contains nulls.
      --unique              Only output counts of unique values.
      --min                 Only output smallest values.
      --max                 Only output largest values.
      --sum                 Only output sums.
      --mean                Only output means.
      --median              Only output medians.
      --stdev               Only output standard deviations.
      --len                 Only output the length of the longest values.
      --freq                Only output lists of frequent values.
      --count               Only output total row count
      -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.

See also: :doc:`../common_arguments`.

Examples
========

Basic use::

    csvstat examples/realdata/FY09_EDU_Recipients_by_State.csv

When an statistic name is passed, only that stat will be printed::

    csvstat --min examples/realdata/FY09_EDU_Recipients_by_State.csv

        1. State Name: None
        2. State Abbreviate: None
        3. Code: 1
        4. Montgomery GI Bill-Active Duty: 435
        5. Montgomery GI Bill- Selective Reserve: 48
        6. Dependents' Educational Assistance: 118
        7. Reserve Educational Assistance Program: 60
        8. Post-Vietnam Era Veteran's Educational Assistance Program: 1
        9. TOTAL: 768
       10. j: None

If a single stat *and* a single column are requested, only a value will be returned::

    csvstat -c 4 --mean examples/realdata/FY09_EDU_Recipients_by_State.csv

    6,263.904
