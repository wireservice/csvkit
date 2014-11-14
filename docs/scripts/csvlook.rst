=======
csvlook
=======

Description
===========

Renders a CSV to the command line in a readable, fixed-width format::

    usage: csvlook [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p` ESCAPECHAR] [-e ENCODING]
                   [FILE]

    Render a CSV file in the console as a fixed-width table.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit

If a table is too wide to display properly try truncating it using :doc:`csvcut`.

If the table is too long, try filtering it down with grep or piping the output to ``less``.

See also: :doc:`../common_arguments`.

Examples
========

Basic use::

    $ csvlook examples/testfixed_converted.csv

This utility is especially useful as a final operation when piping through other utilities::

    $ csvcut -c 9,1 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvlook
