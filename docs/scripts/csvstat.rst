=======
csvstat
=======

Description
===========

Prints descriptive statistics for all columns in a CSV file. Will intelligently determine the type of each column and then print analysis relevant to that type (ranges for dates, mean and median for integers, etc.):

.. code-block:: bash

   usage: csvstat [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                  [-S] [--blanks] [--null-value NULL_VALUES [NULL_VALUES ...]]
                  [--date-format DATE_FORMAT] [--datetime-format DATETIME_FORMAT]
                  [-H] [-K SKIP_LINES] [-v] [-l] [--zero] [-V] [--csv] [--json]
                  [-i INDENT] [-n] [-c COLUMNS] [--type] [--nulls] [--non-nulls]
                  [--unique] [--min] [--max] [--sum] [--mean] [--median]
                  [--stdev] [--len] [--max-precision] [--freq]
                  [--freq-count FREQ_COUNT] [--count]
                  [--decimal-format DECIMAL_FORMAT] [-G] [-y SNIFF_LIMIT] [-I]
                  [FILE]

   Print descriptive statistics for each column in a CSV file.

   positional arguments:
     FILE                  The CSV file to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     --csv                 Output results as a CSV table, rather than plain text.
     --json                Output results as JSON text, rather than plain text.
     -i INDENT, --indent INDENT
                           Indent the output JSON this many spaces. Disabled by
                           default.
     -n, --names           Display column names and indices from the input CSV
                           and exit.
     -c COLUMNS, --columns COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to be examined, e.g. "1,id,3-5". Defaults to
                           all columns.
     --type                Only output data type.
     --nulls               Only output whether columns contains nulls.
     --non-nulls           Only output counts of non-null values.
     --unique              Only output counts of unique values.
     --min                 Only output smallest values.
     --max                 Only output largest values.
     --sum                 Only output sums.
     --mean                Only output means.
     --median              Only output medians.
     --stdev               Only output standard deviations.
     --len                 Only output the length of the longest values.
     --max-precision       Only output the most decimal places.
     --freq                Only output lists of frequent values.
     --freq-count FREQ_COUNT
                           The maximum number of frequent values to display.
     --count               Only output total row count.
     --decimal-format DECIMAL_FORMAT
                           %-format specification for printing decimal numbers.
                           Defaults to locale-specific formatting with "%.3f".
     -G, --no-grouping-separator
                           Do not use grouping separators in decimal numbers.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           Limit CSV dialect sniffing to the specified number of
                           bytes. Specify "0" to disable sniffing entirely, or
                           "-1" to sniff the entire file.
     -I, --no-inference    Disable type inference (and --locale, --date-format,
                           --datetime-format, --no-leading-zeroes) when parsing
                           the input.

See also: :doc:`../common_arguments`.

Examples
========

Basic use:

.. code-block:: bash

   csvstat examples/realdata/FY09_EDU_Recipients_by_State.csv

When an statistic name is passed, only that stat will be printed:

.. code-block:: console

   $ csvstat --min examples/realdata/FY09_EDU_Recipients_by_State.csv
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

If a single stat *and* a single column are requested, only a value will be returned:

.. code-block:: console

   $ csvstat -c 4 --mean examples/realdata/FY09_EDU_Recipients_by_State.csv
   6,263.904
