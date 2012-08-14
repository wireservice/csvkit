=====
csvpy
=====

Description
===========

Loads a CSV file into a :doc:`CSVKitReader </api/csvkit>` object and then drops into a Python shell so the user can inspect the data however they see fit::

    usage: csvpy [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                 [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-v] [--zero]
                 [FILE]

    Load a CSV file into a CSVKitReader object and then drops into a Python shell.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit

This utility will automatically use the IPython shell if it is installed, otherwise it will use the running Python shell.

Also see: :doc:`common_arguments`.

Examples
========

Basic use::

    $ csvpy examples/dummy.csv
    Welcome! Your data has been loaded in a CSVKitReader object named "reader".
    >>> reader.next()
    [u'a', u'b', u'c']

