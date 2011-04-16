========
csvstack
========

Description
===========

Stack up the rows from multiple CSV files, optionally adding a grouping value. Each CSV file must have the same number of columns and they must have the same column names.

Examples
========

Contrived example: joining a set of homogoenous files for different years::

    csvstack -g 1984,1985 -n year examples/testfixed_converted.csv examples/testfixed_converted.csv
