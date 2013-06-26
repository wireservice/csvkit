========
csvgroup
========

Description
===========

Perform a SQL-like group by operation on a csv file on a specified column or columns. For each grouping, the row printed is the row that is first in the lexicographic sorting of the group's rows. Optionally add a new column to indicate how many rows are in each group. Optionally only show the grouped columns in the output::


    usage: csvgroup [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-v] [-l]
                [--zero] [-c COLUMNS] [-a FUNCTION COLUMNS] [-n]
                [FILE]

    Execute a SQL-like group by on specified column or columns

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -c COLUMNS, --columns COLUMNS
                            The column name(s) on which to group by. Should be
                            either one name (or index) or a comma-separated list.
                            May also be left unspecified, in which case none
                            columns will be used
      -a FUNCTION COLUMNS, --aggregation FUNCTION COLUMNS
                            Aggregate column values using max function
      -n, --names           Display column names and indices from the input CSV
                            and exit.

Also see: :doc:`common_arguments`.

Aggregation functions
=====================

 * max
 * min
 * sum
 * count - count every row
 * countA - count non zero rows


Examples
========

Having a data::

    $ csvlook examples/test_group.csv
    |-----+----+----+----+----+-----|
    |  h1 | h2 | h3 | h4 | h5 | h6  |
    |-----+----+----+----+----+-----|
    |  a  | a  | b  | 1  | 2  | 3   |
    |  c  | b  | b  | 0  | 0  | 0   |
    |  d  | b  | b  | 6  | 7  | 1   |
    |  b  | a  | b  | 3  | 2  | 1   |
    |-----+----+----+----+----+-----|

.. warning::

    You should be familiar with ``sort | uniq`` idiom in \*nix, also here you need to always use ``csvsort | csvgroup``.



Lets aggregate by column h2 using  min, max and count of columns h4, h5, h6::

    $ csvsort -c h2 examples/test_group.csv | csvgroup -c h2 -a min h4 -a max h5 -a count h6 | csvlook
    |-----+---------+---------+------------|
    |  h2 | min(h4) | max(h5) | count(h6)  |
    |-----+---------+---------+------------|
    |  a  | 1       | 2       | 2          |
    |  b  | 0       | 7       | 2          |
    |-----+---------+---------+------------|

We can also define many columns for one aggregate::

    $ csvsort -c h2 examples/test_group.csv | csvgroup -c h2 -a max 4-6 | csvlook
    |-----+---------+---------+----------|
    |  h2 | max(h4) | max(h5) | max(h6)  |
    |-----+---------+---------+----------|
    |  a  | 3       | 2       | 3        |
    |  b  | 6       | 7       | 1        |
    |-----+---------+---------+----------|


Aggregating by two columns::

    $ csvsort -c h2,h3 examples/test_group.csv | csvgroup -c h2,h3 -a max 4-6 | csvlook
    |-----+----+---------+---------+----------|
    |  h2 | h3 | max(h4) | max(h5) | max(h6)  |
    |-----+----+---------+---------+----------|
    |  a  | b  | 3       | 2       | 3        |
    |  b  | b  | 6       | 7       | 1        |
    |-----+----+---------+---------+----------|

And by all rows::

    $ csvgroup -a max 4-6 examples/test_group.csv | csvlook
    |----------+---------+----------|
    |  max(h4) | max(h5) | max(h6)  |
    |----------+---------+----------|
    |  6       | 7       | 3        |
    |----------+---------+----------|

