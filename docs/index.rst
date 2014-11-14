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

Table of contents
=================

.. toctree::
    :maxdepth: 3 
    
    install
    tutorial
    cli 
    lib
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

