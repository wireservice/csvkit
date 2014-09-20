================
csvkit |release|
================

About
=====

.. include:: ../README

Why csvkit?
===========

Because it makes your life easier.

Convert Excel to CSV::

    in2csv data.xls > data.csv

Convert JSON to CSV::

    in2csv data.json > data.csv

Print column names::

    csvcut -n data.csv

Select a subset of columns::

    csvcut -c column_a,column_c data.csv > new.csv

Reorder columns::

    csvcut -c column_c,column_a data.csv > new.csv

Find rows with matching ells::

    csvgrep -c phone_number -r 555-555-\d{4}" data.csv > matching.csv

Convert to JSON::

    csvjson data.csv > data.json

Generate summary statistics::

    csvstat data.csv

Query with SQL::

    csvsql --query "select name from data where age > 30" data.csv > old_folks.csv

Import into PostgreSQL::

    csvsql --db postgresql:///database --insert data.csv 

Extract data from PostgreSQL:::

    sql2csv --db postgresql:///database --query "select * from data" > extract.csv

And much more...

Installation
============

Users
-----

csvkit is works on Python versions 2.6, 2.7, 3.3 and 3.4, as well as `PyPy <http://pypy.org/>`_. It is supported on OSX and Linux. It also works--but is tested less frequently--on Windows.

Installing csvkit is simple::

    pip install csvkit

.. note::

    If you are installing on Ubuntu you may need to install the Python development headers prior to install csvkit::

        sudo apt-get install python-dev python-pip python-setuptools build-essential

.. note:: 

    If the installation appears to be successful but running the tools fails, try updating your version of Python setuptools::

        pip install --upgrade setuptools
        pip install --upgrade csvkit

.. note::

    If you are using Python2 and have a recent version of pip, you may need to run pip with the additional arguments :code:`--allow-external argparse`.

Developers
----------

If you are a developer that also wants to hack on csvkit, install it this way::

    git clone git://github.com/onyxfish/csvkit.git
    cd csvkit
    mkvirtualenv csvkit

    # If running Python 2
    pip install -r requirements-py2.txt

    # If running Python 3
    pip install -r requirements-py3.txt

    python setup.py develop
    tox

Be sure to read the documentation below under the header :ref:`contributing`.
    
Tutorial
========

The csvkit tutorial walks through processing and analyzing a real dataset:

.. toctree::
    :maxdepth: 2 
    :numbered:

    tutorial/1_getting_started
    tutorial/2_examining_the_data
    tutorial/3_power_tools
    tutorial/4_going_elsewhere

Usage
=====

csvkit is comprised of a number of individual command line utilities that be loosely divided into a few major categories: Input, Processing, and Output. Documentation and examples for each utility are described on the following pages.

*Input*

.. toctree::
    :maxdepth: 1 

    scripts/in2csv
    scripts/sql2csv

*Processing*

.. toctree::
    :maxdepth: 1 

    scripts/csvclean
    scripts/csvcut
    scripts/csvgrep
    scripts/csvjoin
    scripts/csvsort
    scripts/csvstack

*Output (and Analysis)*
   
.. toctree::
    :maxdepth: 1 

    scripts/csvformat
    scripts/csvjson
    scripts/csvlook
    scripts/csvpy
    scripts/csvsql
    scripts/csvstat

*Appendices*

.. toctree::
    :maxdepth: 2 

    common_arguments
    tricks

Using as a library
==================

csvkit is designed to be used a replacement for most of Python's :mod:`csv` module. Important parts of the API are documented on the following pages.

Don't!

::

    import csv

Do!

::

    import csvkit

.. toctree::
    :maxdepth: 1

    api/csvkit
    api/csvkit.py2
    api/csvkit.py3
    api/csvkit.unicsv
    api/csvkit.sniffer

Principles
==========

csvkit is to tabular data what the standard Unix text processing suite (grep, sed, cut, sort) is to text. As such, csvkit adheres to `the Unix philosophy <http://en.wikipedia.org/wiki/Unix_philosophy>`_.

#. Small is beautiful.
#. Make each program do one thing well.
#. Build a prototype as soon as possible.
#. Choose portability over efficiency.
#. Store data in flat text files.
#. Use software leverage to your advantage.
#. Use shell scripts to increase leverage and portability.
#. Avoid captive user interfaces.
#. Make every program a filter.

As there is no formally defined CSV format, csvkit encourages well-known formatting standards:

* Output favors compatability with the widest range of applications. This means that quoting is done with double-quotes and only when necessary, columns are separated with commas, and lines are terminated with unix style line endings ("\\n").

* Data that is modified or generated will prefer consistency over brevity. Floats always include at least one decimal place, even if they are round. Dates and times are written in ISO8601 format.

.. _contributing:

Contributing
============

Want to hack on csvkit? Here's how:

.. toctree::
    :maxdepth: 2

    contributing
    release 

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Changelog
=========

.. include:: ../CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

