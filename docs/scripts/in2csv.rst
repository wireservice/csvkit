======
in2csv
======

Description
===========

Converts various tabular data formats into CSV.

Converting fixed width requires that you provide a schema file with the "-s" option. The schema file should have the following format::

    column,start,length
    name,0,30
    birthday,30,10
    age,40,3

The header line is required and must match the example exactly::

    usage: in2csv [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p` ESCAPECHAR] [-e ENCODING] [-f FORMAT] [-s SCHEMA]
                  [FILE]

    Convert common, but less awesome, tabular data formats to CSV.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -f FORMAT, --format FORMAT
                            The format of the input file. If not specified will be
                            inferred from the filename. Supported formats: csv,
                            fixed, xls.
      -s SCHEMA, --schema SCHEMA
                            Specifies a CSV-formatted schema file for converting
                            fixed-width files. See documentation for details..

Also see: :doc:`common_arguments`.

Examples
========

Convert a fixed-width file::

    $ in2csv -s examples/testfixed_schema.csv examples/testfixed

Convert an xls file::

    $ in2csv examples/test.xls

Standardize a CSV file::

    $ in2csv examples/bad.csv
