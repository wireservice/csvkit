========
csvgroup
========

Description
===========

Perform a SQL-like group by operation on a csv file on a specified column or columns. For each grouping, the row printed is the row that is first in the lexicographic sorting of the group's rows. Optionally add a new column to indicate how many rows are in each group. Optionally only show the grouped columns in the output.


    usage: csvgroup [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p` ESCAPECHAR] [-e ENCODING] [-c COLUMNS]
		    [-n COUNT_COLUMN_NAME] [-g]
                    FILES [FILES ...]

    Execute a SQL-like group by on a specified column or columns.

    positional arguments:
      FILES                 The CSV files to operate on. If only one is specified,
                            it will be copied to STDOUT.

    optional arguments:
      -h, --help            show this help message and exit
      -c COLUMNS, --columns COLUMNS
                            The column name(s) or index(es) on which to group
			    by.Separate multiple columns by commas. Indexes
			    start at 1. If left unspecified, all columns will be used
      -n COUNT_COLUMN_NAME, --count COUNT_COLUMN_NAME
                            Add a column with the given name for the row count
			    for each group. If no COUNT_COLUMN_NAME is
			    specified, use the name "count"
      -g, --grouped_only    Only include the grouped columns in the output

      Note that grouping reads the entire file into memory. Don't try this on very
      large files.

Also see: :doc:`common_arguments`.
