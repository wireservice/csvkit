=======
csvjoin
=======

Description
===========

Merges two or more CSV tables together using a method analogous to SQL JOIN operation. By default it performs an inner join, but full outer, left outer, and right outer are also available via flags. Key columns are specified with the -c flag (either a single column which exists in all tables, or a comma-separated list of columns with one corresponding to each). If the columns flag is not provided then the tables will be merged "sequentially", that is they will be merged in row order with no filtering:

.. code-block:: none

   usage: csvjoin [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3,4,5}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                  [-S] [--blanks] [--null-value NULL_VALUES [NULL_VALUES ...]]
                  [--date-format DATE_FORMAT] [--datetime-format DATETIME_FORMAT]
                  [--no-leading-zeroes] [-H] [-K SKIP_LINES] [-v]
                  [--output-compression {gzip,bz2,zst}]
                  [--compression-level {1,2,3,4,5,6,7,8,9}] [-l] [--add-bom]
                  [--zero] [-V] [-c COLUMNS] [--outer] [--left] [--right]
                  [-y SNIFF_LIMIT] [-I]
                  [FILE ...]

   Execute a SQL-like join to merge CSV files on a specified column or columns.

   positional arguments:
     FILE                  CSV files to join. A single input is copied to stdout.
                           Input files can use different compression formats.
                           Named files are decompressed by extension: gzip (.gz),
                           bzip2 (.bz2), xz (.xz), or Zstandard (.zst, requires
                           the optional zstandard package).
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
     -c COLUMNS, --columns COLUMNS
                           The column name(s) on which to join. Should be either
                           one name (or index) or a comma-separated list with one
                           name (or index) per file, in the same order in which
                           the files were specified. If not specified, the two
                           files will be joined sequentially without matching.
     --outer               Perform a full outer join, rather than the default
                           inner join.
     --left                Perform a left outer join, rather than the default
                           inner join. If more than two files are provided this
                           will be executed as a sequence of left outer joins,
                           starting at the left.
     --right               Perform a right outer join, rather than the default
                           inner join. If more than two files are provided this
                           will be executed as a sequence of right outer joins,
                           starting at the right.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           Limit CSV dialect sniffing to the specified number of
                           bytes. Specify "0" to disable sniffing entirely, or
                           "-1" to sniff the entire file.
     -I, --no-inference    Disable type inference (and --locale, --date-format,
                           --datetime-format, --no-leading-zeroes) when parsing
                           the input.

   Note that the join operation requires reading all files into memory. Don't try
   this on very large files.

See also: :doc:`../common_arguments`.

Examples
========

.. code-block:: bash

   csvjoin -c 1 examples/join_a.csv examples/join_b.csv

Add two empty columns to the right of a CSV:

.. code-block:: bash

   echo "," | csvjoin examples/dummy.csv -

Add a single column to the right of a CSV:

.. code-block:: bash

   echo "new-column" | csvjoin examples/dummy.csv -
