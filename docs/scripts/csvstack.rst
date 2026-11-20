========
csvstack
========

Description
===========

Stack up the rows from multiple CSV files, optionally adding a grouping value to each row:

.. code-block:: none

   usage: csvstack [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3,4,5}]
                   [-b] [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S]
                   [-H] [-K SKIP_LINES] [-v]
                   [--output-compression {gzip,bz2,zst}]
                   [--compression-level {1,2,3,4,5,6,7,8,9}] [-l] [--add-bom]
                   [--zero] [-V] [-g GROUPS] [-n GROUP_NAME] [--filenames]
                   [FILE ...]

   Stack up the rows from multiple CSV files, optionally adding a grouping value.

   positional arguments:
     FILE                  CSV files to stack. Input files can use different
                           compression formats. Named files are decompressed by
                           extension: gzip (.gz), bzip2 (.bz2), xz (.xz), or
                           Zstandard (.zst, requires the optional zstandard
                           package).
                           Omit FILE or use "-" to read uncompressed CSV from
                           stdin.

   optional arguments:
     -h, --help            show this help message and exit
     --output-compression {gzip,bz2,zst}
                           Compress standard output using gzip, bzip2 or
                           Zstandard (requires the zstandard package).
     --compression-level {1,2,3,4,5,6,7,8,9}
                           Set the compression level (default: 9 for gzip/bz2, 3
                           for zst). Requires --output-compression.
     -g GROUPS, --groups GROUPS
                           A comma-separated list of values to add as "grouping
                           factors", one per CSV being stacked. These are added
                           to the output as a new column. You may specify a name
                           for the new column using the -n flag.
     -n GROUP_NAME, --group-name GROUP_NAME
                           A name for the grouping column, e.g. "year". Only used
                           when also specifying -g.
     --filenames           Use each filename as its grouping value. Overrides -g.
                           For .zst input, use --groups instead.

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
