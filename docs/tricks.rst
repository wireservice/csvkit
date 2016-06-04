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

Most tools use ``STDIN`` as input if no filename is given, but tools that accept multiple inputs like :doc:`scripts/csvjoin` and :doc:`scripts/csvstack` don't. To use ``STDIN`` as an input to these tools, use ``-`` as the filename. For example, these three commands produce the same output::

    csvstat examples/dummy.csv
    cat examples/dummy.csv | csvstat
    cat examples/dummy.csv | csvstat -

``csvstack`` can take a filename and ``STDIN`` as input, for example::

    cat ~/src/csvkit/examples/dummy.csv | csvstack ~/src/csvkit/examples/dummy3.csv -

Alternately, you can pipe in multiple inputs like so::

    csvjoin -c id <(csvcut -c 2,5,6 a.csv) <(csvcut -c 1,7 b.csv)

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

If you use Python 2 on FreeBSD, you may need to install `py-sqlite3 <https://www.freshports.org/databases/py-sqlite3/>`_.

.. note ::

    Need more speed? If you use Python 2, :code:`pip install cdecimal` for a boost.

Unexpected results
------------------

* Are values appearing in incorrect columns?
* Does the output combine multiple fields into a single column with double-quotes?
* Does the outplit split a single field into multiple columns?
* Are `csvstat -c 1` and `csvstat --count` reporting inconsistent row counts?

These may be symptoms of CSV sniffing gone wrong. As there is no single, standard CSV format, csvkit uses Python's `csv.Sniffer <https://docs.python.org/3.5/library/csv.html#csv.Sniffer>`_ to deduce the format of a CSV file: that is, the field delimiter and quote character. By default, the entire file is sent for sniffing, which can be slow. You can send a small sample with the :code:`--snifflimit` option. If you're encountering any cases above, you can try setting :code:`--snifflimit 0` to disable sniffing and set the `--delimiter` and `--quotechar` options yourself.

Although these issues are annoying, in most cases, CSV sniffing Just Works™. Disabling sniffing by default would produce a lot more issues than enabling it by default.

* Are your ``Y``, ``N``, ``T``, or ``F`` values changing to ``1`` or ``0``?
* Are your phone numbers changing to integers and loosing their leading ``+`` or ``0``?
* Is the Italian comune of None becoming a null value?

These may be symptoms of type inference gone wrong. CSV is a text format, but a CSV may contain text representing numbers, dates, booleans or other types. Many csvkit tools try to cast the input text to an appropriate type, in a process called "type inference". Type inference can be slow, however. To disable type inference, use the :code:``--no-inference`` switch. If you want to preserve your original input (with its ``Y``, ``N``, etc.), use :code:``--no-inference``.

Slow performance
----------------

See the above section about setting the :code:``--snifflimit`` option or using the :code:``--no-inference`` switch to improve performance, if the tool supports those options.

Database errors
---------------

Are you seeing this error message, even after running :code:`pip install psycopg2` or :code:`pip install MySQL-python`?

::

    You don't appear to have the necessary database backend installed for connection string you're trying to use. Available backends include:

    Postgresql: pip install psycopg2
    MySQL:      pip install MySQL-python

    For details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at: 

    http://www.sqlalchemy.org/docs/dialects/

First, make sure that you can open a ``python`` interpreter and run :code:`import psycopg2`. If you see an error containing ``mach-o, but wrong architecture``, you may need to reinstall ``psycopg2`` with :code:`export ARCHFLAGS="-arch i386" pip install --upgrade psycopg2` (`source <http://www.destructuring.net/2013/07/31/trouble-installing-psycopg2-on-osx/>`_). If you see another error, you may be able to find a solution on StackOverflow.

