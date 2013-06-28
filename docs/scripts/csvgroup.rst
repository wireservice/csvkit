========
csvgroup
========

Description
===========

Perform a SQL-like group by operation on a CSV file on a specified column or columns. Operation results in printing
columns that were aggregation key (it will be distinct in every row) and appending all columns from aggregation functions values::


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
 * common - returns most common value (handy with text fields aggregation)


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

    Before grouping by any number of columns (see ``-c`` option) you should always sort data using the same columns identifiers ( e.g. use ``csvsort -c 1,2,3 | csvgroup -c 1,2,3``). csvgroup pre assumes that data are already sorted using aggregation key. This is very similar to Linux ``sort`` and ``uniq`` idiom.

    Sorting is however not necessary for grouping without specifying `-c` parameter (without aggregation key).



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

.. note::

    Notice that aggregation by all rows does not require any kind of sorting, because every row is treated as unique.

Get most common value of every column::

    $ csvgroup -a common 1-6 examples/test_group.csv | csvlook
    |-----+----+----+----+----+-----|
    |  h1 | h2 | h3 | h4 | h5 | h6  |
    |-----+----+----+----+----+-----|
    |  a  | a  | b  | 1  | 2  | 1   |
    |-----+----+----+----+----+-----|


