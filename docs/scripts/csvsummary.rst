==========
csvsummary
==========

Description
===========

Prints descriptive statistics for all columns in a CSV file. Will intelligently determine the type of each column and then print analysis relevant to that type (ranges for dates, mean and median for integers, etc.)::

    usage: csvsummary [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                      [-p` ESCAPECHAR] [-e ENCODING]
                      [FILE]

    Print descriptive statistics for all columns in a CSV file.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit

Also see: :doc:`common_arguments`.

Examples
========

Basic use::

    $ csvsummary examples/testfixed_converted.csv
