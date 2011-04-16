======
in2csv
======

Description
===========

Converts various formats into csv. Currently supported: fixed-width and xls (Excel).

Converting fixed width requires that you provide a schema file with the "-s" option. The schema file should have the following format::

    column,start,length
    name,0,30
    birthday,30,10
    age,40,3

The header line is required and must match exactly.

All output from in2csv is written to standard out.

Examples
========

Convert a fixed-width file::

    in2csv -s examples/testfixed_schema.csv examples/testfixed

Convert an xls file::

    in2csv examples/test.xls

