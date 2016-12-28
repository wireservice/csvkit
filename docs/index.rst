================
csvkit |release|
================

About
=====

.. include:: ../README.rst

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

Find rows with matching cells::

    csvgrep -c phone_number -r "555-555-\d{4}" data.csv > new.csv

Convert to JSON::

    csvjson data.csv > data.json

Generate summary statistics::

    csvstat data.csv

Query with SQL::

    csvsql --query "select name from data where age > 30" data.csv > new.csv

Import into PostgreSQL::

    csvsql --db postgresql:///database --insert data.csv

Extract data from PostgreSQL::

    sql2csv --db postgresql:///database --query "select * from data" > new.csv

And much more...

Table of contents
=================

.. toctree::
    :maxdepth: 3

    tutorial
    cli
    tricks
    contributing
    release
    license
    changelog

Citation
========

When citing csvkit in publications, you may use this BibTeX entry::

    @Manual{,
      title = {csvkit},
      author = {Christopher Groskopf and contributors},
      year = 2016,
      url = {https://csvkit.readthedocs.org/}
    }

Authors
=======

.. include:: ../AUTHORS.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
