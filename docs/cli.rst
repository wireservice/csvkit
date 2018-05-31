=========
Reference
=========

csvkit is composed of command-line tools that can be divided into three major categories: Input, Processing, and Output. Documentation and examples for each tool are described on the following pages.

Input
=====

.. toctree::
    :maxdepth: 1

    scripts/in2csv
    scripts/sql2csv

Processing
==========

.. toctree::
    :maxdepth: 1

    scripts/csvclean
    scripts/csvcut
    scripts/csvgrep
    scripts/csvjoin
    scripts/csvsort
    scripts/csvstack

To transpose CSVs, consider `csvtool <http://colin.maudry.com/csvtool-manual-page/>`_. Install ``csvtool`` on Linux using your package manager, or on macOS using::

    brew install ocaml
    opam install csv
    ln -s ~/.opam/system/bin/csvtool /usr/local/bin/
    csvtool --help

To run ``sed``-like commands on CSV files, consider `csvsed <https://github.com/metagriffin/csvsed>`_.

Output and Analysis
===================

.. toctree::
    :maxdepth: 1

    scripts/csvformat
    scripts/csvjson
    scripts/csvlook
    scripts/csvpy
    scripts/csvsql
    scripts/csvstat

To diff CSVs, consider `daff <https://github.com/paulfitz/daff>`_. An alternative to :doc:`csvsql` is `q <https://github.com/harelba/q>`_.

Common arguments
================

.. toctree::
    :maxdepth: 2

    common_arguments
