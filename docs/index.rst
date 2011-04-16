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

* Do not modify input data unless specifically requested by the user (i.e. conversion).

* When modifying input data, conform to good standards. Floats should end with ".0", even if they are round, dates and times should be in ISO8601 format, etc.

Installation
============

For developers::

    git clone git://github.com/onyxfish/csvkit.git
    cd csvkit
    mkvirtualenv --no-site-packages csvkit
    pip install -r requirements.txt
    nosetests

For users (until first PyPI build is ready)::

    git://github.com/onyxfish/csvkit.git
    cd csvkit
    python setup.py install

Usage
=====

.. toctree::
    :maxdepth: 1 

    scripts/in2csv
    scripts/csvclean
    scripts/csvcut
    scripts/csvjoin
    scripts/csvlook
    scripts/csvsql
    scripts/csvstack
    scripts/csvsummary

Development
===========

Developer documentation coming soon...

Authors
=======

* Christopher Groskopf
* Joe Germuska
* Aaron Bycoffe

License
=======

.. include:: ../COPYING

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

