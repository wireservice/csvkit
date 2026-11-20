=======
csvsort
=======

Description
===========

Sort CSV files. Like the Unix "sort" command, but for tabular data:

.. code-block:: none

   usage: csvsort [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3,4,5}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                  [-S] [--blanks] [--null-value NULL_VALUES [NULL_VALUES ...]]
                  [--date-format DATE_FORMAT] [--datetime-format DATETIME_FORMAT]
                  [--no-leading-zeroes] [-H] [-K SKIP_LINES] [-v]
                  [--output-compression {gzip,bz2,zst}]
                  [--compression-level {1,2,3,4,5,6,7,8,9}] [-l] [--add-bom]
                  [--zero] [-V] [-n] [-c COLUMNS] [-r] [-i] [-y SNIFF_LIMIT] [-I]
                  [FILE]

   Sort CSV files. Like the Unix "sort" command, but for tabular data.

   positional arguments:
     FILE                  CSV file to read. Named files are decompressed by
                           extension: gzip (.gz), bzip2 (.bz2), xz (.xz), or
                           Zstandard (.zst, requires the optional zstandard
                           package).
                           Omit FILE or use "-" to read uncompressed CSV from
                           stdin. For .zst input, use --snifflimit 0 and specify
                           --tabs or --delimiter if needed.

   optional arguments:
     -h, --help            show this help message and exit
     --output-compression {gzip,bz2,zst}
                           Compress standard output using gzip, bzip2 or
                           Zstandard (requires the zstandard package).
     --compression-level {1,2,3,4,5,6,7,8,9}
                           Set the compression level (default: 9 for gzip/bz2, 3
                           for zst). Requires --output-compression.
     -n, --names           Display column names and indices from the input CSV
                           and exit.
     -c COLUMNS, --columns COLUMNS
                           A comma-separated list of column indices, names or
                           ranges to sort by, e.g. "1,id,3-5". Defaults to all
                           columns.
     -r, --reverse         Sort in descending order.
     -i, --ignore-case     Perform case-independent sorting.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           Limit CSV dialect sniffing to the specified number of
                           bytes. Specify "0" to disable sniffing entirely, or
                           "-1" to sniff the entire file.
     -I, --no-inference    Disable type inference (and --locale, --date-format,
                           --datetime-format, --no-leading-zeroes) when parsing
                           the input.

See also: :doc:`../common_arguments`.

.. note::

    If your file is large, try :code:`sort -t, file.csv` instead.

Examples
========

Sort the veteran's education benefits table by the "TOTAL" column:

.. code-block:: bash

   csvsort -c 9 examples/realdata/FY09_EDU_Recipients_by_State.csv

View the five states with the most individuals claiming veteran's education benefits:

.. code-block:: bash

   csvcut -c 1,9 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsort -r -c 2 | head -n 5
