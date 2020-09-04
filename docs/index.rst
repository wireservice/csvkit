================
csvkit |release|
================

About
=====

.. include:: ../README.rst

First time? See :doc:`tutorial`.

.. note::

    To change the field separator, line terminator, etc. of the **output**, you must use :doc:`/scripts/csvformat`.

.. note::

    csvkit, by default, `sniffs <https://docs.python.org/3.5/library/csv.html#csv.Sniffer>`_ CSV formats (it deduces whether commas, tabs or spaces delimit fields, for example), and performs type inference (it converts text to numbers, dates, booleans, etc.). These features are useful and work well in most cases, but occasional errors occur. If you don't need these features, set :code:`--snifflimit 0` (:code:`-y 0`) and :code:`--no-inference` (:code:`-I`).

.. note::

    If you need to do more complex data analysis than csvkit can handle, use `agate <https://github.com/wireservice/agate>`_. If you need csvkit to be faster or to handle larger files, you may be reaching the limits of csvkit. Consider loading the data into SQL, or using `xsv <https://github.com/BurntSushi/xsv>`_.

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
