======
csvcut
======

Description
===========

Filters and truncates CSV files. Like unix "cut" command, but for tabular data.

Note that csvcut does not include row slicing or filtering, for this you should pipe data to head, tail, or grep.

Examples
========

Print the indices and names of all columns::

    csvcut -n examples/testfixed_converted.csv

Extract the first and third columns::

    csvcut -c 1,3 examples/testfixed_converted.csv

Extract columns named "integer" and "date"::

    csvcut -c integer,date examples/testfixed_converted.csv

Show the first ten values in column 1::

    csvcut -c 1 -s examples/testfixed_converted.csv | head -n 10

Show the last value in column 6::

    csvcut -c 6 -s examples/testfixed_converted.csv | tail -n 1

Show unique values in the fourth column::

    csvcut -c 4 -s examples/testfixed_converted.csv | uniq

Search for rows about Chicago::

    csvcut -s examples/testfixed_converted.csv | grep -i chicago

Add line-numbers to the csvcut output, then find the Chicago Tribune::

    csvcut -l -s examples/testfixed_converted.csv | grep -i tribune
