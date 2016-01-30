========================
Tips and Troubleshooting
========================

Tips
====

Reading compressed CSVs
-----------------------

csvkit has builtin support for reading ``gzip`` or ``bz2`` compressed input files. This is automatically detected based on the file extension. For example::

    csvstat examples/dummy.csv.gz
    csvstat examples/dummy.csv.bz2

Please note, the files are decompressed in memory, so this is a convenience, not an optimization.

Specifying STDIN as a file
--------------------------

Most tools default to ``STDIN`` if no filename is specified, but tools like :doc:`scripts/csvjoin` and :doc:`scripts/csvstack` accept multiple files, so this is not possible. To work around this it is also possible to specify ``STDIN`` by using ``-`` as a filename. For example, these three commands are functionally identical::

    csvstat examples/dummy.csv
    cat examples/dummy.csv | csvstat
    cat examples/dummy.csv | csvstat -

This specification allows you to, for instance, ``csvstack`` input on ``STDIN`` with another file::

    cat ~/src/csvkit/examples/dummy.csv | csvstack ~/src/csvkit/examples/dummy3.csv -

Troubleshooting
===============

Installation
------------

csvkit is supported on:

* Python 2.7+
* Python 3.3+
* `PyPy <http://pypy.org/>`_

It is tested on OS X, and has been used on Linux and Windows.

If installing on Ubuntu, you may need to install Python's development headers first::

    sudo apt-get install python-dev python-pip python-setuptools build-essential
    pip install csvkit

If the installation is successful but csvkit's tools fail, you may need to update Python's setuptools package first::

    pip install --upgrade setuptools
    pip install --upgrade csvkit

If you use Python 2 and have a recent version of pip, you may need to run pip with :code:`--allow-external argparse`.

.. note ::

    Need more speed? If you use Python 2, :code:`pip install cdecimal` for a boost.

