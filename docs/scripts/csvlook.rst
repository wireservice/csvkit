=======
csvlook
=======

Description
===========

Renders a CSV to the command line in a readable, fixed-width format. If the table is too long, try piping the output to head, tail, more or less.

Examples
========

Basic use::

    csvlook examples/testfixed_converted.csv

This is especially useful when piping through other utilities::

    csvcut -c 2,3 -l examples/testfixed_converted.csv | csvlook
