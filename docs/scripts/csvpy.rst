=====
csvpy
=====

Description
===========

Loads a CSV file into a :class:`agate.csv.Reader` object and then drops into a Python shell so the user can inspect the data however they see fit::

    usage: csvpy [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                 [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v]
                 [--dict]
                 [FILE]

    Load a CSV file into a CSV reader and then drop into a Python shell.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      --dict                Use a CSV DictReader instead of a normal reader.

This tool will automatically use the IPython shell if it is installed, otherwise it will use the running Python shell.

.. note::

    Due to platform limitations, csvpy does not accept file input on STDIN. 

See also: :doc:`../common_arguments`.

Examples
========

Basic use::

    csvpy examples/dummy.csv
    Welcome! "examples/dummy.csv" has been loaded in a reader object named "reader".
    >>> reader.next()
    [u'a', u'b', u'c']

As a dictionary::

    csvpy --dict examples/dummy.csv -v
    Welcome! "examples/dummy.csv" has been loaded in a DictReader object named "reader".
    >>> reader.next()
    {u'a': u'1', u'c': u'3', u'b': u'2'}

