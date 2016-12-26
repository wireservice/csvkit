=======
csvjoin
=======

Description
===========

Merges two or more CSV tables together using a method analogous to SQL JOIN operation. By default it performs an inner join, but full outer, left outer, and right outer are also available via flags. Key columns are specified with the -c flag (either a single column which exists in all tables, or a comma-separated list of columns with one corresponding to each). If the columns flag is not provided then the tables will be merged "sequentially", that is they will be merged in row order with no filtering::

    usage: csvjoin [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v] [-l]
                   [--zero] [-c COLUMNS] [--outer] [--left] [--right]
                   [FILE [FILE ...]]

    Execute a SQL-like join to merge CSV files on a specified column or columns.

    positional arguments:
      FILE                  The CSV files to operate on. If only one is specified,
                            it will be copied to STDOUT.

    optional arguments:
      -h, --help            show this help message and exit
      -c COLUMNS, --columns COLUMNS
                            The column name(s) on which to join. Should be either
                            one name (or index) or a comma-separated list with one
                            name (or index) for each file, in the same order that
                            the files were specified. May also be left
                            unspecified, in which case the two files will be
                            joined sequentially without performing any matching.
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

    Note that the join operation requires reading all files into memory. Don't try
    this on very large files.

See also: :doc:`../common_arguments`.

Examples
========

::

    csvjoin -c 1 examples/join_a.csv examples/join_b.csv

This command says you have two files to outer join, file1.csv and file2.csv. The key column in file1.csv is ColumnKey, the key column in file2.csv is Column Key.

Add two empty columns to the right of a CSV::

    echo "," | csvjoin examples/dummy.csv -
