===============
Tips and Tricks
===============

Reading compressed CSVs
=======================

csvkit has builtin support for reading ``gzip`` or ``bz2`` compressed input files. This is automatically detected based on the file extension. For example::

    $ csvstat examples/dummy.csv.gz
    $ csvstat examples/dummy.csv.bz2

Please note, the files are decompressed in memory, so this is a convenience, not an optimization.

Specifying STDIN as a file
==========================

Most tools default to ``STDIN`` if no filename is specified, but tools like :doc:`scripts/csvjoin` and :doc:`scripts/csvstack` accept multiple files, so this is not possible. To work around this it is also possible to specify ``STDIN`` by using ``-`` as a filename. For example, these three commands are functionally identical::

    $ csvstat examples/dummy.csv
    $ cat examples/dummy.csv | csvstat
    $ cat examples/dummy.csv | csvstat -

This specification allows you to, for instance, ``csvstack`` input on ``STDIN`` with another file::

    $ cat ~/src/csvkit/examples/dummy.csv | csvstack ~/src/csvkit/examples/dummy3.csv -

