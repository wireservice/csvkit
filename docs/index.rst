================
csvkit |release|
================

About
=====

.. include:: ../README

Principles
==========

csvkit has been developed with a number of guiding principles in mind:

* Produce compatability-oriented output. This means that quoting is done with double-quotes and only when necessary, columns are separated with commas, and lines are terminated with unix style line endings ("\n").

* Stream output to STDOUT to support Unix piping. As an example, the following would display the top 10 rows, columns 1 and 3 only, of a Excel xls file that has been converted to csv::

    in2csv data.xls | csvcut -c 1,3 | head 10

* Do not modify input data unless specifically requested by the user (i.e. conversion or error cleaning).

* When modifying input data, conform to good standards. Floats should end with ".0", even if they are round, dates and times should be in ISO8601 format, etc.

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

Tutorial
========

Tutorial coming soon...

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
    scripts/csvjoin
    scripts/csvstack

*Output and Analysis*
   
.. toctree::
    :maxdepth: 1 

    scripts/csvlook
    scripts/csvsql
    scripts/csvsummary

*Appendices*

.. toctree::
    :maxdepth: 1 

    scripts/common_arguments

Development
===========

Developer documentation coming soon...

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

