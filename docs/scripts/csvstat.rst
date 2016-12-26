=======
csvstat
=======

Description
===========

Prints descriptive statistics for all columns in a CSV file. Will intelligently determine the type of each column and then print analysis relevant to that type (ranges for dates, mean and median for integers, etc.)::

    usage: csvstat [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-H] [-v]
                   [--zero] [-y SNIFFLIMIT] [-c COLUMNS] [--max] [--min] [--sum]
                   [--mean] [--median] [--stdev] [--nulls] [--unique] [--freq]
                   [--len] [--count]
                   [FILE]

    Print descriptive statistics for each column in a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be examined. Defaults to all columns.
      --max                 Only output max.
      --min                 Only output min.
      --sum                 Only output sum.
      --mean                Only output mean.
      --median              Only output median.
      --stdev               Only output standard deviation.
      --nulls               Only output whether column contains nulls.
      --unique              Only output counts of unique values.
      --freq                Only output frequent values.
      --len                 Only output max value length.
      --count               Only output row count

See also: :doc:`../common_arguments`.

Examples
========

Basic use::

    csvstat examples/realdata/FY09_EDU_Recipients_by_State.csv

When an statistic name is passed, only that stat will be printed::

    csvstat --freq examples/realdata/FY09_EDU_Recipients_by_State.csv

      1. State Name: None
      2. State Abbreviate: None
      3. Code: None
      4. Montgomery GI Bill-Active Duty: 3548.0
      5. Montgomery GI Bill- Selective Reserve: 1019.0
      6. Dependents' Educational Assistance: 1261.0
      7. Reserve Educational Assistance Program: 715.0
      8. Post-Vietnam Era Veteran's Educational Assistance Program: 6.0
      9. TOTAL: 6520.0
     10. _unnamed: None
 
If a single stat *and* a single column are requested, only a value will be returned::

    csvstat -c 4 --freq examples/realdata/FY09_EDU_Recipients_by_State.csv

    3548.0

