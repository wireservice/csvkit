========
csvstack
========

Description
===========

Stack up the rows from multiple CSV files, optionally adding a grouping value to each row:

.. code-block:: none

   usage: csvstack [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                   [-K SKIP_LINES] [-v] [-l] [--zero] [-V] [-g GROUPS]
                   [-n GROUP_NAME] [--filenames]
                   [FILE [FILE ...]]

   Stack up the rows from multiple CSV files, optionally adding a grouping value.

   positional arguments:
     FILE                  The CSV file(s) to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     -g GROUPS, --groups GROUPS
                           A comma-separated list of values to add as "grouping
                           factors", one per CSV being stacked. These are added
                           to the output as a new column. You may specify a name
                           for the new column using the -n flag.
     -n GROUP_NAME, --group-name GROUP_NAME
                           A name for the grouping column, e.g. "year". Only used
                           when also specifying -g.
     --filenames           Use the filename of each input file as its grouping
                           value. When specified, -g will be ignored.

See also: :doc:`../common_arguments`.

.. warning::

    If you redirect output to an input file like :code:`csvstack file.csv > file.csv`, the file will grow indefinitely.

Examples
========

Join a set of files for different years:

.. code-block:: bash

   csvstack -g 2009,2010 examples/realdata/FY09_EDU_Recipients_by_State.csv examples/realdata/Datagov_FY10_EDU_recp_by_State.csv

Add a single column to the left of a CSV:

.. code-block:: bash

   csvstack -n NEWCOL -g "" examples/dummy.csv
