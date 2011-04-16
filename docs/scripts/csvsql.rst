======
csvsql
======

Description
===========

Generates a SQL "CREATE TABLE" statement for a given CSV file. Supports a variety of SQL dialects (execute "csvsql -h" for a complete list).

Examples
========

Generate a statement in the postgresql dialect::

    csvsql -i postgresql examples/testfixed_converted.csv
