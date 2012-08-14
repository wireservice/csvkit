================
csvkit |release|
================

About
=====

.. include:: ../README

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

Installation
============

For users::

    pip install csvkit

For developers::

    git clone git://github.com/onyxfish/csvkit.git
    cd csvkit
    mkvirtualenv --no-site-packages csvkit
    pip install -r requirements.txt
    nosetests

.. note::

    csvkit is routinely tested on OSX, somewhat less frequently on Linux and once in a while on Windows. All platforms are supported. It is tested against Python 2.6, 2.7 and PyPy. Neither Python < 2.6 nor Python >= 3.0 are supported at this time.

Tutorial
========

The csvkit tutorial walks through processing and analyzing a real dataset from `data.gov <http://data.gov>`_. It is divided into several parts for easier reading:

.. toctree::
    :maxdepth: 2 
    :numbered:

    tutorial/getting_started
    tutorial/examining_the_data
    tutorial/adding_another_year
    tutorial/wrapping_up

Usage
=====

csvkit is comprised of a number of individual command line utilities that be loosely divided into a few major categories: Input, Processing, and Output. Documentation and examples for each utility are described on the following pages.

*Input*

.. toctree::
    :maxdepth: 1 

    scripts/in2csv

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

    scripts/csvjson
    scripts/csvlook
    scripts/csvpy
    scripts/csvsql
    scripts/csvstat

*Appendices*

.. toctree::
    :maxdepth: 1 

    scripts/common_arguments

Development
===========

csvkit is designed to augment or supercede much of Python's :mod:`csv` module. Important parts of the API are documented here:

.. toctree::
    :maxdepth: 1

    api/csvkit
    api/csvkit.unicsv
    api/csvkit.sniffer

Contributing
============

Want to hack on csvkit? Here's how:

.. toctree::
    :maxdepth: 2

    contributing

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

